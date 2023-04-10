from requests import request, Response
from bs4 import BeautifulSoup
from datetime import datetime
from argparse import ArgumentParser, SUPPRESS
from typing import Self

FOURCHAN_IMAGE_CDN = "https://i.4cdn.org"
FOURCHAN_JSON_CDN = "https://a.4cdn.org"
FOURCHAN_BOARD_URL = "https://boards.4channel.org"

class FourChanScraper:
    # (private) __write_file__ - Writes data )bytes) as file to disk
    def __write_file__(self: Self, name: str, content: bytes) -> None:
        with open(name, "wb") as w:
            if w.writable():
                w.write(content)

    # (private): Print error message and exit  
    def __error__(self: Self, err: str) -> None:
        print(f"Error: {err}")
        exit()

    # (private): Create a get request through requests module 
    def __get_requ__(self: Self, url: str) -> Response:
        ask = request("GET", url)

        if ask.status_code != 200:
            self.__error__(
                f"GET request failed. Status code: {ask.status_code}"
            )

        return ask

    # (unused): Scrap a page for images (if any)
    def __unused_front_scrape__(self: Self, board: str, page: int) -> None:
        url = f"{FOURCHAN_BOARD_URL}/{board}/{page}"
        resp = self.__get_requ__(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        sfa = soup.find_all("a", attrs={ "class": "fileThumb" })

        for each in sfa:
            img_url = each.get("href").replace("//", "https://")
            file_name = img_url.replace(f"{FOURCHAN_IMAGE_CDN}/{board}/", "")
            resp = self.__get_requ__(img_url)

            print(f"Got: {file_name}")
            self.__write_file__(file_name, resp.content)

    # (public): Scrap any image page of a specific page (if any)
    def chan_page_images(self: Self, board: str, page: int) -> None:
        if page < 1:
            self.__error__("Page number can't be zero or negative")

        url = f"{FOURCHAN_JSON_CDN}/{board}/{page}.json"
        resp = self.__get_requ__(url)

        for list_iter_one in resp.json()["threads"]: # "threads" doesn't implies user created threads 
            for list_iter_two in list_iter_one["posts"]:
                if "tim" and "ext" in list_iter_two:
                    file_name = f"{list_iter_two['tim']}{list_iter_two['ext']}"
                    url = f"{FOURCHAN_IMAGE_CDN}/{board}/{file_name}"
                    resp = self.__get_requ__(url)

                    print(f"Got: {file_name}")
                    self.__write_file__(file_name, resp.content)

    # (public): Scrap all images of a specific thread (if any)
    def chan_thread_images(self: Self, board: str, thread_id: int) -> None:
        url = f"{FOURCHAN_JSON_CDN}/{board}/thread/{thread_id}.json"
        resp = self.__get_requ__(url)

        for each in resp.json()["posts"]:
            if "tim" and "ext" in each:
                file_name = f"{each['tim']}{each['ext']}"
                url = f"{FOURCHAN_IMAGE_CDN}/{board}/{file_name}"
                resp = self.__get_requ__(url)

                print(f"Got: {file_name}")
                self.__write_file__(file_name, resp.content)

    # (public): Scrap all threads on a page and look for images (if any)
    def chan_all_threads_images(self: Self, board: str, page: int) -> None:
        if page <= 1:
            url = f"{FOURCHAN_BOARD_URL}/{board}"
            resp = self.__get_requ__(url)
        else:
            url = f"{FOURCHAN_BOARD_URL}/{board}/{page}"
            resp = self.__get_requ__(url)

        soup = BeautifulSoup(resp.text, "html.parser")
        sfi = soup.find_all("div", attrs={ "class": "thread" })

        for each in sfi:
            scrap_id = each["id"].removeprefix("t")
            url = f"{FOURCHAN_JSON_CDN}/{board}/thread/{scrap_id}.json"
            resp = self.__get_requ__(url)

            for each in resp.json()["posts"]:
                if "tim" and "ext" in each:
                    file_name = f"{each['tim']}{each['ext']}"
                    url = f"{FOURCHAN_IMAGE_CDN}/{board}/{file_name}"
                    resp = self.__get_requ__(url)

                    print(f"Got: {file_name}")
                    self.__write_file__(file_name, resp.content)

    # (public): Scrap all comments on a page (if any)
    def chan_page_comments(self: Self, board: str, page: int) -> None:
        if page < 1:
            self.__error__("Page number can't be zero or negative")\

        url = f"{FOURCHAN_JSON_CDN}/{board}/{page}.json"
        resp = self.__get_requ__(url)

        for list_iter_one in resp.json()["threads"]:
            for list_iter_two in list_iter_one["posts"]:
                if "com" in list_iter_two:
                    print(
                        f"ID: {list_iter_two['no']}\n"
                        f"User: {list_iter_two['name']}\n"
                        f"Time: {datetime.fromtimestamp(list_iter_two['time'])}\n"
                        f"Comment: {list_iter_two['com']}\n"
                    )

    # (public): Scrap all comments of a specific thread (if any)
    def chan_thread_comments(self: Self, board: str, thread_id: int) -> None:
        url = f"{FOURCHAN_JSON_CDN}/{board}/thread/{thread_id}.json"
        resp = self.__get_requ__(url)

        for each in resp.json()["posts"]:
            if "com" in each:
                print(
                    f"ID: {each['no']}\n"
                    f"User: {each['name']}\n"
                    f"Time: {datetime.fromtimestamp(each['time'])}\n"
                    f"Comment: {each['com']}\n"
                )

    # (public): Scrap all threads on a page and look for comments (if any)
    def chan_all_threads_comments(self: Self, board: str, page: int) -> None:
        if page < 1:
            self.__error__("Page number can't be zero or negative")

        if page == 1:
            url = f"{FOURCHAN_BOARD_URL}/{board}"
            resp = self.__get_requ__(url)
        else:
            url = f"{FOURCHAN_BOARD_URL}/{board}/{page}"
            resp = self.__get_requ__(url)

        soup = BeautifulSoup(resp.text, "html.parser")
        sfi = soup.find_all("div", attrs={ "class": "thread" })

        for each in sfi:
            scrap_id = each["id"].removeprefix("t")
            url = f"{FOURCHAN_JSON_CDN}/{board}/thread/{scrap_id}.json"
            resp = self.__get_requ__(url)

            for each in resp.json()["posts"]:
                if "com" in each:
                    print(
                        f"ID: {each['no']}\n"
                        f"User: {each['name']}\n"
                        f"Time: {datetime.fromtimestamp(each['time'])}\n"
                        f"Comment: {each['com']}\n"
                    )

# Main access function
def main():
    parser = ArgumentParser(
        add_help=False,
        usage=SUPPRESS
    )

    chan = FourChanScraper()

    # Add arguments
    parser.add_argument(
        "--page-images",
        action="store_true",
        dest="page_images",
        help="Scrap all images on a page"
    )

    parser.add_argument(
        "--thread-images",
        action="store_true",
        dest="thread_images",
        help="Scrap all images of a specific thread"
    )

    parser.add_argument(
        "--all-threads-images",
        action="store_true",
        dest="all_threads_images",
        help="Scrap all threads on a page and look for images"
    )

    parser.add_argument(
        "--page-comments",
        action="store_true",
        dest="page_comments",
        help="Scrap all comments on a page"
    )

    parser.add_argument(
        "--thread-comments",
        action="store_true",
        dest="thread_comments",
        help="Scrap all comments of a specific thread"
    )

    parser.add_argument(
        "--all-threads-comments",
        action="store_true",
        dest="all_threads_comments",
        help="Scrap all threads on a page and look for comments"
    )

    parser.add_argument(
        "--board",
        type=str
    )

    parser.add_argument(
        "--page",
        type=int
    )

    parser.add_argument(
        "--thread",
        type=int
    )

    args = parser.parse_args()

    # Check for arguments
    chan.chan_page_images(
        board=args.board, page=args.page
    ) if args.page_images == True else None
    
    chan.chan_thread_images(
        board=args.board, thread_id=args.thread
    ) if args.thread_images == True else None

    chan.chan_all_threads_images(
        board=args.board, page=args.page
    ) if args.all_threads_images == True else None

    chan.chan_page_comments(
        board=args.board, page=args.page
    ) if args.page_comments == True else None

    chan.chan_thread_comments(
        board=args.board, thread_id=args.thread
    ) if args.thread_comments == True else None

    chan.chan_all_threads_comments(
        board=args.board, page=args.page
    ) if args.all_threads_comments == True else None

main()
