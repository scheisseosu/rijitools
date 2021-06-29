import requests, sys
from bs4 import BeautifulSoup
from structs import Board, Topic, Reply

domain = "https://rijihuudu.ahlamontada.com"

def scrape(options):
    riji_home_html = requests.get(domain).text

    rijisoup = BeautifulSoup(riji_home_html, 'html.parser')

    html_boards = rijisoup.find_all(name="li", class_="row")
    boards = []
    for b in html_boards:
        linked_title = b.find(class_="forumtitle")
        board_url = domain + linked_title['href']
        boards.append(Board(linked_title.string, board_url))

    


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("Usage: scraper.py [options]")
        print("\t-o [filename]\tOutput collected data to a file")
        print("\t-u           \tOnly collect user info")
        print("\t-b [board]   \tEnter a comma-separated list of boards to include")

        sys.exit(0)

    options = {}

    try:
        options['outputf'] = None
        if "-o" in args:
            options['outputf'] = args[args.index("-o")+1]
        
        options['users_only'] = "-u" in args

        options['selected_boards'] = None
        if "-b" in args:
            options['selected_board'] = args[args.index("-b")+1].split(",")

    except Exception as e:
        print(f"Error on argument processing, use \"python scraper.py -h\" for usage:\n\n{e}")
    
    scrape(options)
    



    

