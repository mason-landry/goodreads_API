import requests
import sqlite3
import xml.etree.ElementTree as ET
import xlrd

KEY = "MY_KEY"
conn = sqlite3.connect('my_database.db')

def create_tables():
    '''Call this function without inputs to make our initial tables in your SQL database'''
    conn.execute('CREATE TABLE ratings (title TEXT, author TEXT, avg_rating REAL, num_ratings INTEGER, rating_dist TEXT)')

def get_book_statistics(book_title: str, author: str):
    '''Queries Goodreads API with book_title and author_name, adding rating statistics to our SQL database'''
    try:
        # Build URL based on Goodreads API documentation
        url = f'https://www.goodreads.com/book/title.xml'
        # Build headers using parameters descriped for API method
        params = {"key": KEY, "title": book_title, "author": author}
        res = requests.get(url, params=params)  # Send API request
        root = ET.fromstring(res.text)  # Feed returned XML data into parser
        book = root.find("book")  # Find book by its tag
        book_rating = book.find("average_rating").text
        work = book.find("work")
        ratings_count = work.find("ratings_count").text
        rating_dist = work.find("rating_dist").text

        # We can extract author info as presented on Goodreads as follows:
        authors = book.find('authors')  # o to Authors tag in XML
        author = []
        for child in authors:   # In many cases there will be multiple authors
            author.append(child.find('name').text)

        return book_rating, ratings_count, rating_dist, author
    except:
        print("failed to get stats for book", book_title)

def import_books(fil):
    '''Input XLSX file of book search results from Springer, and this fn will query Goodreads API to get some rating statistics and add them to SQL database'''
    book = xlrd.open_workbook(fil)
    sheet = book.sheet_by_name("Sheet1")
    N = sheet.nrows
    # Import only the 1st column, and all rows except column headings
    titles = [sheet.cell_value(r, 0) for r in range(1, N)]
    # Import only the 7th column, and all rows except column headings
    authors = [sheet.cell_value(r, 6) for r in range(1, N)]

    for t in range(len(titles)):
        try:
            # Test to see if it is already in DB
            check = conn.execute("select title from ratings where title=?", (titles[t],)).fetchone()
            if check:
                pass    # Book is already in database
            else:
                # Quick loop to extract first author's name from jumbled authors string
                a = authors[t]
                for i in range(1, len(a)):
                    if a[i] == a[i].upper() and a[i-1] == a[i-1].lower() and a[i] != ' ' and a[i-1] != ' ':
                        author = a[0:i]
                        break
                    else:   # In case there is only one author:
                        author = a
                book_rating, ratings_count, rating_dist, author = get_book_statistics(titles[t], author)
                conn.execute("insert into ratings(title, author, avg_rating, num_ratings, rating_dist) values (?,?,?,?,?)", (titles[t], author[0], book_rating, ratings_count, str(rating_dist)))
                print("added ratings from book", titles[t])
                conn.commit()
        except:
            Exception("Failed to import book", titles[t])

def get_author_id(author_name):
    '''uses Goodreads API to get author URL using only author's name, and returns the first GoodReads author id'''
    try:
        # Build URL:
        url = f'https://www.goodreads.com/api/author_url/{author_name}'
        params = {"key": KEY}
        res = requests.get(url, params=params)
        res_xml = res.text  # res.text returns XML data
        root = ET.fromstring(res_xml)
        # author_id is stored in root[1] 
        author_id = root[1].attrib["id"]
        return author_id
    except:
        Exception("Could not get author id")

def add_books_by_author(author_id):
    '''This function takes in a Goodreads author id and requests all books written by that author. It will add these books to our sqlite3 database'''
    url = f'https://www.goodreads.com/author/list.xml'  # Build URL based on Goodreads API documentation
    # Build headers using parameters descriped for API method
    params = {"key": KEY, "id": author_id}
    res = requests.get(url, params=params)  # Send API request
    root = ET.fromstring(res.text)  # Feed returned XML data into parser
    books = root.findall(".//book")  # Find all book tags in XML

    # Loop through all books found in XML:
    for book in books:
        title = book.find('title').text  # Get text for book title
        isbn = book.find('isbn').text   # Get text for isbn

        # Since 'authors' tag has sub-tags, need to jump down another level to get author data
        # You can determine the structure/layout easily by looking at the HTML in browser
        authors = book.find('authors')
        # Grab the name of the first author, in case it is different from our original input
        author = authors[0][1].text

        # Now to add the book and details to our SQL table:
        check = conn.execute("select title from books where title=? and author=?", (
            title, author,)).fetchone()    # Test to see if it is already in DB
        if check:
            pass    # Book is already in database
        else:
            conn.execute("insert into books(title, author, author_id, isbn) values (?,?,?,?)",
                         (title, author, author_id, isbn))
            conn.commit()

def get_books_by_author(author_id):
    '''This function takes in a Goodreads author id and returns all book titles written by that author.'''
    url = f'https://www.goodreads.com/author/list.xml'  # Build URL based on Goodreads API documentation
    # Build headers using parameters descriped for API method
    params = {"key": KEY, "id": author_id}
    res = requests.get(url, params=params)  # Send API request
    root = ET.fromstring(res.text)  # Feed returned XML data into parser
    books = root.findall(".//book")  # Find all book tags in XML

    # Loop through all books found in XML:
    titles = []
    for book in books:
        titles.append(book.find('title').text)  # Get text for book title

    return titles

if __name__ == "__main__":
    create_tables()
    import_books("SearchResults.xlsx")
    titles = conn.execute("select title from ratings").fetchall()
    for b in books:
        print(b)