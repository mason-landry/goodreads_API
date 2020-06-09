import sqlite3
conn = sqlite3.connect('my_database.db')

if __name__ == "__main__":
    data = conn.execute("select * from ratings").fetchall()
    titles = [d[0] for d in data]
    authors = [d[0] for d in data]
    avg_ratings = [d[2] for d in data]
    num_ratings = [d[3] for d in data]
    rating_dists = [d[4] for d in data]
    print('Highest rated book is', titles[avg_ratings.index(max(avg_ratings))], "with rating", max(avg_ratings), "with rating distribution:", rating_dists[avg_ratings.index(max(avg_ratings))])
    print('Most Reviewed book is', titles[num_ratings.index(max(num_ratings))], "with", max(num_ratings), "ratings")
    # Let's look at maybe a more useful metric: avg_rating * num_ratings
    sum_ratings = []
    for i in range(len(avg_ratings)):
        sum_ratings.append(avg_ratings[i]*(num_ratings[i]))

    print('Best book overall is', titles[sum_ratings.index(max(sum_ratings))], "with rating", avg_ratings[sum_ratings.index(max(sum_ratings))] , "with rating distribution:", rating_dists[sum_ratings.index(max(sum_ratings))])
    
    #List the top 10 books overall
    overall = [i for i in sum_ratings]
    overall.sort(reverse=True)
    for i in range(10):
        print(titles[sum_ratings.index(overall[i])], avg_ratings[sum_ratings.index(overall[i])], rating_dists[sum_ratings.index(overall[i])])


        