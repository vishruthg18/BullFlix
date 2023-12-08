from flask import redirect, render_template, request, session, Blueprint, url_for
from db import connection

ratings_blueprint = Blueprint('ratings', __name__)

@ratings_blueprint.route('/movies/<string:movie_id>/rate-movie', methods=['GET', 'POST'])
def rate_movie(movie_id):
    session['user_id'] = 'B32E80410A2C4FEAAE7D856F715477BC' # for testing purposes only, remove this line when done testing
    session['username'] = 'test' # for testing purposes only, remove this line when done testing

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    movie_title = None

    cursor = connection.cursor()
    
    try:
        # get movie title
        sql_query = "SELECT movie_title FROM rmdb.movies WHERE movie_guid = HEXTORAW(:movie_hex_guid)"
        cursor.execute(sql_query, {"movie_hex_guid":movie_id})
        result = cursor.fetchone()
        movie_title = result[0] if result else None
        cursor.close()

        if movie_title == None:
            return "Movie not found."

        # check if user has already rated the movie
        cursor = connection.cursor()
        sql_query = "SELECT rating FROM bullflix.ratings WHERE user_guid = HEXTORAW(:user_hex_guid) AND movie_guid = HEXTORAW(:movie_hex_guid)"
        cursor.execute(sql_query, {"user_hex_guid":user_id, "movie_hex_guid":movie_id})
        result = cursor.fetchone()
        previous_rating = result[0] if result else None
        cursor.close()
    except Exception as e:
        return f"Error: {str(e)}"
    
    
    if request.method == 'POST':
        rating = request.form['rating']
        
        if rating == '':
            return "Please enter a rating."
        if int(rating) < 1 or int(rating) > 5:
            return "Please enter a rating between 1 and 5."
        
        try:
            cursor = connection.cursor()

            if previous_rating != None:
                # update rating
                sql_query = "UPDATE bullflix.ratings SET rating = :rating WHERE user_guid = HEXTORAW(:user_hex_guid) AND movie_guid = HEXTORAW(:movie_hex_guid)"
                cursor.execute(sql_query, {"rating":rating, "user_hex_guid":user_id, "movie_hex_guid":movie_id})
                connection.commit()
                cursor.close()
                print("Rating updated successfully.")
                return redirect(url_for('index'))
            
            sql_query = "INSERT INTO bullflix.ratings(user_guid, movie_guid, rating) VALUES (HEXTORAW(:user_hex_guid), HEXTORAW(:movie_hex_guid), :rating)"
            cursor.execute(sql_query, {"rating":rating, "user_hex_guid":user_id, "movie_hex_guid":movie_id})
            connection.commit()
            cursor.close()
            print("Rating added successfully.")
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('rate-movie.html', movie_id=movie_id, movie_title=movie_title, previous_rating=previous_rating)

@ratings_blueprint.route('/all-movies', methods=['GET'])
def display_movies():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bullflix.movies ORDER BY title ASC LIMIT 100")
        movies = cursor.fetchall()
        cursor.close()
        return render_template('movies.html', movies=movies)
    except Exception as e:
        return f"Error: {str(e)}"
    
 

# Show movies that the user has rated    
@ratings_blueprint.route('/rated-movies', methods=['GET'])
def display_rated_movies():
    session['user_id'] = 'B32E80410A2C4FEAAE7D856F715477BC' # for testing purposes only, remove this line when done testing
    session['username'] = 'test' # for testing purposes only, remove this line when done testing

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    try:
        cursor = connection.cursor()
        sql_query="""
        SELECT 
            movie_hex_guid,
            movie_title,
            release_year,
            rating,
            rating_date 
        FROM bullflix.ratings_vw
            WHERE user_hex_guid = :user_id
        ORDER BY rating DESC
        """
        cursor.execute(sql_query, {"user_id":user_id})
        movies = cursor.fetchall()
        cursor.close()
        return render_template('rated-movies.html', rated_movies=movies)
    except Exception as e:
        return f"Error: {str(e)}"

@ratings_blueprint.route('/popular-movies', methods=['GET'])
def display_popular_movies():
    session['user_id'] = 'B32E80410A2C4FEAAE7D856F715477BC' # for testing purposes only, remove this line when done testing
    session['username'] = 'test' # for testing purposes only, remove this line when done testing

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    try:
        cursor = connection.cursor()
        sql_query="""
        SELECT
            movie_guid,
            movie_title,
            release_year,
            imdb_rating,
            imdb_votes
        FROM
            bullflix.recommendations
            INNER JOIN sqlmdb.movies
            USING (movie_guid)
        WHERE
            user_guid = HEXTORAW(:user_id)
        ORDER BY 
            imdb_rating DESC, imdb_votes DESC
        """
        cursor.execute(sql_query, {"user_id":user_id})
        movies = cursor.fetchall()
        cursor.close()
        return render_template('popular-movies.html', popular_movies=movies)
    except Exception as e:
        return f"Error: {str(e)}"
    