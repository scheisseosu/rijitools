import requests, sys, time
from bs4 import BeautifulSoup
from structs import Board, Topic, Reply

domain = "https://rijihuudu.ahlamontada.com"

def scrape(options):
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
            scrape_board(board, quiet=options['quiet'])
        print()

    #Get users


def scrape_board(board, quiet=True):
    #Progress report
    if not quiet:
        print(f"Processing {board.name:>20.20}...",end="\r")
    board_page_html = requests.get(board.url).text

    


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("Usage: scraper.py [options]")
        print("\t-o [filename]\tOutput collected data to a file")
        print("\t-u           \tOnly collect user info")
        print("\t-b [board]   \tEnter a comma-separated list of boards to include (use _ for spaces)")
        print("\t-q           \tQuiet (run without progress output")

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

    except Exception as e:
        print(f"Error on argument processing, use \"python scraper.py -h\" for usage:\n\n{e}")
    
    scrape(options)
    



    

