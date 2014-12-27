import os
import feedparser
import sqlite3

from config import urls


def extract_rss_link(url):
    os.system(['clear', 'cls'][os.name == 'nt'])
    print "Searching indeed ..."
    listings = feedparser.parse(url)
    print "Found {} listings.".format(len(listings.entries))
    return listings


def add_to_database(all_listings):
    # create database and table (if necessary)
    con = sqlite3.connect('listings.sqlite')
    with con:
        cur = con.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE listings(
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    company TEXT,
                    city TEXT,
                    state TEXT,
                    date_published TEXT
                )
                """
            )
        except sqlite3.OperationalError:
            pass
        counter = 0
        # loop through scrapped listings
        for listing in all_listings.entries:
            url = listing.link
            cur.execute("SELECT * FROM listings where url = ?", (url,))
            check = cur.fetchone()
            # if url is not in db, add it to the db and to the list
            if check is None:
                counter += 1
                title = listing.title_detail.value.split('-')[0]
                company = listing.title_detail.value.split('-')[1]
                location = listing.title_detail.value.split('-')[2]
                try:
                    city = location.split(',')[0]
                    state = location.split(',')[1]
                except:
                    city = 'N/A'
                    state = 'N/A'
                date_published = listing.published
                cur.execute(
                    """
                    INSERT INTO listings(
                        title, url, company, city, state, date_published
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?
                    )
                    """, (title, url, company, city, state, date_published,)
                )
        return counter


if __name__ == '__main__':

    for url in urls:
        rss_results = extract_rss_link(url)
        if rss_results:
            added = add_to_database(rss_results)
            print "{0} listing(s) added to the database!".format(added)
            print "Done!"
