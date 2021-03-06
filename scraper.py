import requests, sys, re, pickle
from bs4 import BeautifulSoup
from .structs import Board, Topic, Reply, User

sys.setrecursionlimit(50000)

domain = "https://rijihuudu.ahlamontada.com"
users = {} 

default_ops = {
    'outputf':None,
    'users_only':False,
    'selected_boards':None,
    'quiet':False,
    'topic_limit':None
}

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

#Return a list of Board objects from rijihuudu.ahlamontada
def scrape(options=default_ops):
    riji_home_html = requests.get(domain).text

    rijisoup = BeautifulSoup(riji_home_html, 'html.parser')


    boards = None
    if not options['users_only']:
        html_boards = rijisoup.find_all(name="li", class_="row")
        all_boards = []
        for b in html_boards:
            linked_title = b.find(class_="forumtitle")
            board_url = domain + linked_title['href']
            all_boards.append(Board(linked_title.string, board_url))

        boards = []
        if options['selected_boards']:
            for b in all_boards:
                if b.name.lower() in options['selected_boards']:
                    boards.append(b)
        else:
            #use all boards
            boards = all_boards
        
        #Scan through topics to fill board properties
        for board in boards:
            scrape_board(board, quiet=options['quiet'], topic_limit=options['topic_limit'])
        print()
    
        if options['outputf']:
            with open(f"{options['outputf']}.txt", "w", encoding='utf-8') as f:
                for b in boards:
                    f.write(repr(b)+"\n")
                    for t in b.topics:
                        f.write("\t"+repr(t)+"\n")
                        for r in t.replies:
                            f.write("\t\t"+repr(r)+"\n")
            #pickle objects
            save_object(boards, f"{options['outputf']}.pkl")

    return boards
    


    


def scrape_board(board, quiet=True, topic_limit=None):
    global users

    board_page_html = requests.get(board.url).text

    boardsoup = BeautifulSoup(board_page_html, 'html.parser')

    #Count number of pages on board
    pages = boardsoup.find(class_="pagination")
    if pages.a:
        #has pages
        pages = int(pages.a.find_all('strong')[1].string)
    else:
        #only front page
        pages = 1
    board.pages = pages

    #Iterate through topics for each page
    page_iterations = board.pages
    if topic_limit:
        page_iterations = 1
    
    for i in range(1,page_iterations+1):

        #Get the contents of current page
        page_html = None
        if i==1:
            #Use already pulled page html
            page_html = board_page_html
        else:
            page_html = requests.get(board.page_url(i)).text
        pagesoup = BeautifulSoup(page_html, 'html.parser')

        html_topics = pagesoup.find_all(name="li", class_=re.compile("row"))
        
        #cap number of html topics to process
        if topic_limit:
            html_topics = html_topics[:topic_limit]

        #Create object for each html topic item
        numtop = len(html_topics)
        count = 0

        for t in html_topics:
            
            #PROGRESS
            if not quiet:
                prog = count/float(numtop)
                bar = f"[{'???'*int(prog*50)}{'-'*int(50-(prog*50))}]"
                print(f"Processing {board.name:>20.20}... Page [{i}/{board.pages}]\t{bar}",end="\r")

            #need url, title, description, content, author
            titleelem = t.find(class_="topictitle")
            url = domain+ titleelem['href']

            #check title formatting
            formatted = titleelem.find('span')
            title = ""
            if formatted:
                title = formatted.string
            else:
                title = titleelem.string
            
            #get title description
            description = titleelem.find(class_="topic-description")
            if description:
                #access the string
                description = description.string

            #FIXME: pull user obj for author after creating userlist
            author = t.find(class_="topic-author").string
            if not author:
                #none or (most likely) multiple strings in elem, due to formatting
                author = t.find(class_="topic-author").stripped_strings
                author = ' '.join(author)
            #strip to username
            author = author[author.index("by")+3:]
            
            #set up user obj for author
            users.setdefault(author, User(author))
            authorobj = users[author]
            
            #Initialize topic item with no content
            topicobj = Topic(url, title, description, None, authorobj)
            
            #Scrape through topic page to fill attribs
            scrape_topic(topicobj)

            #Add completed topic to board
            board.add_topic(topicobj)
            count+= 1
    print(board)


#Enumerate topic object, creating reply objects and content
def scrape_topic(topic):
    topic_page_html = requests.get(topic.url).text
    topicsoup = BeautifulSoup(topic_page_html, 'html.parser')

    #collect list of posts in topic, excluding sponsored posts (id="p0")
    posts = topicsoup.find_all(name="div", id=re.compile("^p[1-9][0-9]*"))

    #Get time of topic op
    datestr = posts[0].find(name="div", class_="topic-date").string
    #Fix time on posts with rep
    if not datestr:
        datestr = posts[0].find(name="div", class_="topic-date").get_text()
    topic.set_time(datestr)

    #Set topic content
    topic.content = get_post_content(posts[0])

    #ensure topic's author has pfp (since it cant be found from topic listing)
    if not topic.author.pfp:
        #record the pfp url source for this author
        urlext = posts[0].find(class_='postprofile-avatar').find(name='img')['src']
        topic.author.set_pfp(domain+urlext)

    #iterate through replies (if any exist)
    if len(posts)>1:
        for reply in posts[1:]:
            try:
                title = reply.find(class_="topic-title").a.string
            except AttributeError:
                continue
            content = get_post_content(reply)

            author = reply.find(class_='postprofile-name')
            #Catch guest accounts (don't have /a/ elems)
            if author.a:
                author = author.a
            author = author.string
            
            if not author:
                #special formatting
                author = reply.find(class_='postprofile-name').find(name='strong').string
            
            #get author object
            users.setdefault(author, User(author))
            authorobj = users[author]

            if not authorobj.pfp:
                #record the pfp url source for this author
                urlext = reply.find(class_='postprofile-avatar').find(name='img')['src']
                authorobj.set_pfp(domain+urlext)
            
            replyobj = Reply(title, content, authorobj, topic)
            #update time attrib
            datestr = reply.find(class_="topic-date").string
            #fix date on replies with rep
            if not datestr:
                datestr =reply.find(name="div", class_="topic-date").get_text()
            replyobj.set_time(datestr)

            #Add completed reply to topic
            topic.add_reply(replyobj)
    
            
    




#get the content of a BS post object
def get_post_content(post):
    content_iter = post.find(class_="content").strings
    content = ""
    for cnt in content_iter:
        content+=cnt+"\n"
    content = content[:-2] #strip last newline char
    return content


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-t" in args:
        #TESTING
        top = Topic("https://rijihuudu.ahlamontada.com/t348-any-___-ers-in-chat", "ATENNTION", "this is mostly for my big stiste rif your not my big stist er GET OUT", None, "\\f")
        scrape_topic(top)
        sys.exit(0)

    if "-h" in args or "--help" in args:
        print("Usage: scraper.py [options]")
        print("\t-o [filename]  \tOutput collected data to a file")
        print("\t-u             \tOnly collect user info")
        print("\t-b [board]     \tEnter a comma-separated list of boards to include (use _ for spaces)")
        print("\t-q             \tQuiet (run without progress output")
        print("\t-n [num topics]\tMaximum number of topics to scrape from each board")

        sys.exit(0)

    options = {}

    try:
        options['outputf'] = None
        if "-o" in args:
            options['outputf'] = args[args.index("-o")+1]
        
        options['users_only'] = "-u" in args

        options['selected_boards'] = None
        if "-b" in args:
            options['selected_boards'] = args[args.index("-b")+1].split(",")
            #clean selections
            cleaned = []
            for b in options['selected_boards']:
                cleaned.append(b.strip().lower().replace("_", " "))
            options['selected_boards'] = cleaned
        
        options['quiet'] = "-q" in args

        options['topic_limit'] = None
        if "-n" in args:
            options['topic_limit'] = int(args[args.index("-n")+1])

    except Exception as e:
        print(f"Error on argument processing, use \"python scraper.py -h\" for usage:\n\n{e}")
    
    scrape(options)
    



    

