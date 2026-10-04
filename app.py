from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort
)

import mysql.connector
from mysql.connector import Error

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from dotenv import load_dotenv

import os
import uuid


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "friendship-secret-key"
)


# =========================================================
# UPLOAD SETTINGS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}


# =========================================================
# ALLOWED FILE
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    return mysql.connector.connect(

        host=os.getenv(
            "DB_HOST",
            "localhost"
        ),

        port=int(
            os.getenv(
                "DB_PORT",
                "3306"
            )
        ),

        user=os.getenv(
            "DB_USER",
            "root"
        ),

        password=os.getenv(
            "DB_PASSWORD",
            ""
        ),

        database=os.getenv(
            "DB_NAME",
            "friendship_db"
        )
    )


# =========================================================
# LOGIN CHECK
# =========================================================

def login_required():

    if "user_id" not in session:

        flash(
            "Please login first."
        )

        return False

    return True


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user():

    if "user_id" not in session:
        return None

    db = None
    cursor = None

    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = %s
            """,
            (
                session["user_id"],
            )
        )

        return cursor.fetchone()

    except Error as e:

        print(
            "Current user error:",
            e
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        age = request.form.get(
            "age",
            ""
        )

        gender = request.form.get(
            "gender",
            ""
        )

        city = request.form.get(
            "city",
            ""
        ).strip()

        interests = request.form.get(
            "interests",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:

            flash(
                "Please enter your name."
            )

            return redirect(
                url_for("register")
            )


        if not email:

            flash(
                "Please enter your email."
            )

            return redirect(
                url_for("register")
            )


        if not password:

            flash(
                "Please enter a password."
            )

            return redirect(
                url_for("register")
            )


        if len(password) < 6:

            flash(
                "Password must be at least 6 characters."
            )

            return redirect(
                url_for("register")
            )


        try:

            age = int(age)

        except (ValueError, TypeError):

            flash(
                "Please enter a valid age."
            )

            return redirect(
                url_for("register")
            )


        if age < 13:

            flash(
                "You must be at least 13 years old."
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )


        db = None
        cursor = None

        try:

            db = get_db()

            cursor = db.cursor(
                dictionary=True
            )


            # -------------------------------------------------
            # CHECK EMAIL
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (
                    email,
                )
            )

            existing_user = cursor.fetchone()


            if existing_user:

                flash(
                    "This email is already registered."
                )

                return redirect(
                    url_for("register")
                )


            # -------------------------------------------------
            # INSERT USER
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    age,
                    gender,
                    city,
                    interests,
                    bio
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    name,
                    email,
                    hashed_password,
                    age,
                    gender,
                    city,
                    interests,
                    bio
                )
            )


            db.commit()


            flash(
                "Account created successfully. Please login."
            )


            return redirect(
                url_for("login")
            )


        except Error as e:

            print(
                "Registration database error:",
                e
            )

            if db:
                db.rollback()

            flash(
                "Database error. Please try again."
            )


        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # If already logged in
    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        if not email or not password:

            flash(
                "Please enter email and password."
            )

            return redirect(
                url_for("login")
            )


        db = None
        cursor = None

        try:

            db = get_db()

            cursor = db.cursor(
                dictionary=True
            )


            # -------------------------------------------------
            # FIND USER
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (
                    email,
                )
            )


            user = cursor.fetchone()


            # -------------------------------------------------
            # CHECK PASSWORD
            # -------------------------------------------------

            if user and check_password_hash(
                user["password"],
                password
            ):

                # Clear old session
                session.clear()


                # Store logged-in user
                session["user_id"] = user["id"]

                session["user_name"] = user["name"]

                session["user_email"] = user["email"]


                flash(
                    "Login successful!"
                )


                # IMPORTANT:
                # LOGIN -> DASHBOARD

                return redirect(
                    url_for("dashboard")
                )


            flash(
                "Invalid email or password."
            )


        except Error as e:

            print(
                "Login database error:",
                e
            )

            flash(
                "Database connection error."
            )


        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )


    search = request.args.get(
        "search",
        ""
    ).strip()

    city = request.args.get(
        "city",
        ""
    ).strip()

    interest = request.args.get(
        "interest",
        ""
    ).strip()


    db = None
    cursor = None

    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        query = """
            SELECT
                id,
                name,
                age,
                gender,
                city,
                interests,
                bio,
                profile_photo

            FROM users

            WHERE id != %s
        """


        values = [
            session["user_id"]
        ]


        # -------------------------------------------------
        # SEARCH BY NAME
        # -------------------------------------------------

        if search:

            query += """
                AND name LIKE %s
            """

            values.append(
                "%" + search + "%"
            )


        # -------------------------------------------------
        # SEARCH BY CITY
        # -------------------------------------------------

        if city:

            query += """
                AND city LIKE %s
            """

            values.append(
                "%" + city + "%"
            )


        # -------------------------------------------------
        # SEARCH BY INTEREST
        # -------------------------------------------------

        if interest:

            query += """
                AND interests LIKE %s
            """

            values.append(
                "%" + interest + "%"
            )


        query += """
            ORDER BY id DESC
        """


        cursor.execute(
            query,
            tuple(values)
        )


        users = cursor.fetchall()


        return render_template(
            "dashboard.html",
            users=users,
            search=search,
            city=city,
            interest=interest
        )


    except Error as e:

        print(
            "Dashboard error:",
            e
        )

        flash(
            "Could not load dashboard."
        )

        return redirect(
            url_for("home")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile/<int:user_id>"
)
def profile(user_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    db = None
    cursor = None

    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = %s
            """,
            (
                user_id,
            )
        )


        user = cursor.fetchone()


        if not user:

            flash(
                "User not found."
            )

            return redirect(
                url_for("dashboard")
            )


        return render_template(
            "profile.html",
            user=user
        )


    except Error as e:

        print(
            "Profile error:",
            e
        )

        flash(
            "Could not load profile."
        )

        return redirect(
            url_for("dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# EDIT PROFILE
# =========================================================

@app.route(
    "/edit-profile",
    methods=["GET", "POST"]
)
def edit_profile():

    if not login_required():

        return redirect(
            url_for("login")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        # =====================================================
        # POST - UPDATE PROFILE
        # =====================================================

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            age = request.form.get(
                "age",
                ""
            )

            gender = request.form.get(
                "gender",
                ""
            )

            city = request.form.get(
                "city",
                ""
            ).strip()

            interests = request.form.get(
                "interests",
                ""
            ).strip()

            bio = request.form.get(
                "bio",
                ""
            ).strip()


            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            if not name:

                flash(
                    "Please enter your name."
                )

                return redirect(
                    url_for("edit_profile")
                )


            try:

                age = int(age)

            except (ValueError, TypeError):

                flash(
                    "Please enter a valid age."
                )

                return redirect(
                    url_for("edit_profile")
                )


            if age < 13:

                flash(
                    "Age must be at least 13."
                )

                return redirect(
                    url_for("edit_profile")
                )


            # -------------------------------------------------
            # GET OLD PROFILE PHOTO
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT profile_photo
                FROM users
                WHERE id = %s
                """,
                (
                    session["user_id"],
                )
            )


            old_user = cursor.fetchone()


            profile_photo = None


            if old_user:

                profile_photo = old_user[
                    "profile_photo"
                ]


            # -------------------------------------------------
            # PROFILE PHOTO UPLOAD
            # -------------------------------------------------

            file = request.files.get(
                "profile_photo"
            )


            if file and file.filename:

                if not allowed_file(
                    file.filename
                ):

                    flash(
                        "Invalid image format. Use JPG, PNG, GIF or WEBP."
                    )

                    return redirect(
                        url_for("edit_profile")
                    )


                # Create unique filename

                extension = file.filename.rsplit(
                    ".",
                    1
                )[1].lower()


                filename = (
                    uuid.uuid4().hex
                    + "."
                    + extension
                )


                filename = secure_filename(
                    filename
                )


                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )


                file.save(
                    file_path
                )


                # -------------------------------------------------
                # DELETE OLD PHOTO
                # -------------------------------------------------

                if profile_photo:

                    old_file_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        profile_photo
                    )


                    if os.path.exists(
                        old_file_path
                    ):

                        try:

                            os.remove(
                                old_file_path
                            )

                        except OSError:

                            pass


                profile_photo = filename


            # -------------------------------------------------
            # UPDATE DATABASE
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE users

                SET
                    name = %s,
                    age = %s,
                    gender = %s,
                    city = %s,
                    interests = %s,
                    bio = %s,
                    profile_photo = %s

                WHERE id = %s
                """,
                (
                    name,
                    age,
                    gender,
                    city,
                    interests,
                    bio,
                    profile_photo,
                    session["user_id"]
                )
            )


            db.commit()


            # Update session name

            session["user_name"] = name


            flash(
                "Profile updated successfully."
            )


            return redirect(
                url_for(
                    "profile",
                    user_id=session["user_id"]
                )
            )


        # =====================================================
        # GET - SHOW EDIT PROFILE
        # =====================================================

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = %s
            """,
            (
                session["user_id"],
            )
        )


        user = cursor.fetchone()


        if not user:

            session.clear()

            flash(
                "User account not found."
            )

            return redirect(
                url_for("login")
            )


        return render_template(
            "edit_profile.html",
            user=user,
            current_user=user
        )


    except Error as e:

        print(
            "Edit profile database error:",
            e
        )

        if db:

            db.rollback()


        flash(
            "Could not update profile."
        )


        return redirect(
            url_for("edit_profile")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADD FRIEND
# =========================================================

@app.route(
    "/add-friend/<int:user_id>"
)
def add_friend(user_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    current_user = session[
        "user_id"
    ]


    if current_user == user_id:

        flash(
            "You cannot add yourself."
        )

        return redirect(
            url_for("dashboard")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # CHECK USER EXISTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
            """,
            (
                user_id,
            )
        )


        target_user = cursor.fetchone()


        if not target_user:

            flash(
                "User not found."
            )

            return redirect(
                url_for("dashboard")
            )


        # -------------------------------------------------
        # CHECK FRIENDSHIP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM friendships

            WHERE
                user1_id = %s
                AND user2_id = %s

            OR
                user1_id = %s
                AND user2_id = %s
            """,
            (
                min(current_user, user_id),
                max(current_user, user_id),

                min(current_user, user_id),
                max(current_user, user_id)
            )
        )


        friendship = cursor.fetchone()


        if friendship:

            flash(
                "You are already friends."
            )

            return redirect(
                url_for("dashboard")
            )


        # -------------------------------------------------
        # CHECK FRIEND REQUEST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                sender_id,
                receiver_id,
                status

            FROM friend_requests

            WHERE
                (
                    sender_id = %s
                    AND receiver_id = %s
                )

                OR

                (
                    sender_id = %s
                    AND receiver_id = %s
                )

            ORDER BY id DESC
            LIMIT 1
            """,
            (
                current_user,
                user_id,

                user_id,
                current_user
            )
        )


        existing = cursor.fetchone()


        if existing:

            # -------------------------------------------------
            # PENDING
            # -------------------------------------------------

            if existing["status"] == "pending":

                if existing["sender_id"] == current_user:

                    flash(
                        "Friend request already sent."
                    )

                else:

                    flash(
                        "This person has already sent you a friend request. Check Requests."
                    )

                return redirect(
                    url_for("dashboard")
                )


            # -------------------------------------------------
            # REJECTED
            # -------------------------------------------------

            if existing["status"] == "rejected":

                cursor.execute(
                    """
                    UPDATE friend_requests

                    SET
                        sender_id = %s,
                        receiver_id = %s,
                        status = 'pending'

                    WHERE id = %s
                    """,
                    (
                        current_user,
                        user_id,
                        existing["id"]
                    )
                )

                db.commit()


                flash(
                    "Friend request sent again."
                )


                return redirect(
                    url_for("dashboard")
                )


        # -------------------------------------------------
        # NEW REQUEST
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO friend_requests
            (
                sender_id,
                receiver_id,
                status
            )

            VALUES
            (
                %s,
                %s,
                'pending'
            )
            """,
            (
                current_user,
                user_id
            )
        )


        db.commit()


        flash(
            "Friend request sent!"
        )


    except Error as e:

        print(
            "Add friend error:",
            e
        )

        if db:
            db.rollback()

        flash(
            "Could not send friend request."
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for("dashboard")
    )


# =========================================================
# FRIEND REQUESTS
# =========================================================

@app.route("/requests")
def requests():

    if not login_required():

        return redirect(
            url_for("login")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # INCOMING REQUESTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT

                fr.id,
                fr.sender_id,
                fr.receiver_id,
                fr.created_at,

                u.name,
                u.age,
                u.gender,
                u.city,
                u.interests,
                u.bio,
                u.profile_photo

            FROM friend_requests fr

            JOIN users u
                ON fr.sender_id = u.id

            WHERE
                fr.receiver_id = %s
                AND fr.status = 'pending'

            ORDER BY fr.created_at DESC
            """,
            (
                session["user_id"],
            )
        )


        requests_list = cursor.fetchall()


        # -------------------------------------------------
        # OUTGOING REQUESTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT

                fr.id,
                fr.sender_id,
                fr.receiver_id,
                fr.created_at,

                u.name,
                u.age,
                u.gender,
                u.city,
                u.interests,
                u.bio,
                u.profile_photo

            FROM friend_requests fr

            JOIN users u
                ON fr.receiver_id = u.id

            WHERE
                fr.sender_id = %s
                AND fr.status = 'pending'

            ORDER BY fr.created_at DESC
            """,
            (
                session["user_id"],
            )
        )


        outgoing_requests = cursor.fetchall()


        return render_template(
            "requests.html",
            requests=requests_list,
            outgoing_requests=outgoing_requests
        )


    except Error as e:

        print(
            "Requests error:",
            e
        )

        flash(
            "Could not load friend requests."
        )

        return redirect(
            url_for("dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ACCEPT FRIEND REQUEST
# =========================================================

@app.route(
    "/accept/<int:request_id>"
)
def accept_request(request_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                sender_id,
                receiver_id

            FROM friend_requests

            WHERE
                id = %s
                AND receiver_id = %s
                AND status = 'pending'
            """,
            (
                request_id,
                session["user_id"]
            )
        )


        friend_request = cursor.fetchone()


        if not friend_request:

            flash(
                "Friend request not found."
            )

            return redirect(
                url_for("requests")
            )


        sender = friend_request[
            "sender_id"
        ]

        receiver = friend_request[
            "receiver_id"
        ]


        # -------------------------------------------------
        # UPDATE REQUEST
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE friend_requests

            SET status = 'accepted'

            WHERE id = %s
            """,
            (
                request_id,
            )
        )


        # -------------------------------------------------
        # CREATE FRIENDSHIP
        # -------------------------------------------------

        user1 = min(
            sender,
            receiver
        )

        user2 = max(
            sender,
            receiver
        )


        cursor.execute(
            """
            SELECT id
            FROM friendships
            WHERE
                user1_id = %s
                AND user2_id = %s
            """,
            (
                user1,
                user2
            )
        )


        existing_friendship = cursor.fetchone()


        if not existing_friendship:

            cursor.execute(
                """
                INSERT INTO friendships
                (
                    user1_id,
                    user2_id
                )

                VALUES
                (
                    %s,
                    %s
                )
                """,
                (
                    user1,
                    user2
                )
            )


        db.commit()


        flash(
            "Friend request accepted!"
        )


    except Error as e:

        print(
            "Accept request error:",
            e
        )

        if db:
            db.rollback()

        flash(
            "Could not accept friend request."
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for("requests")
    )


# =========================================================
# REJECT FRIEND REQUEST
# =========================================================

@app.route(
    "/reject/<int:request_id>"
)
def reject_request(request_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor()


        cursor.execute(
            """
            UPDATE friend_requests

            SET status = 'rejected'

            WHERE
                id = %s
                AND receiver_id = %s
                AND status = 'pending'
            """,
            (
                request_id,
                session["user_id"]
            )
        )


        db.commit()


        flash(
            "Friend request rejected."
        )


    except Error as e:

        print(
            "Reject request error:",
            e
        )

        if db:
            db.rollback()

        flash(
            "Could not reject request."
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for("requests")
    )


# =========================================================
# FRIENDS
# =========================================================

@app.route("/friends")
def friends():

    if not login_required():

        return redirect(
            url_for("login")
        )


    user_id = session[
        "user_id"
    ]


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT

                u.id,
                u.name,
                u.email,
                u.age,
                u.gender,
                u.city,
                u.interests,
                u.bio,
                u.profile_photo

            FROM friendships f

            JOIN users u

            ON
                (
                    u.id = f.user1_id
                    AND f.user2_id = %s
                )

                OR

                (
                    u.id = f.user2_id
                    AND f.user1_id = %s
                )

            ORDER BY u.name ASC
            """,
            (
                user_id,
                user_id
            )
        )


        friends_list = cursor.fetchall()


        return render_template(
            "friends.html",
            friends=friends_list
        )


    except Error as e:

        print(
            "Friends error:",
            e
        )

        flash(
            "Could not load friends."
        )

        return redirect(
            url_for("dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# REMOVE FRIEND
# =========================================================

@app.route(
    "/remove-friend/<int:user_id>"
)
def remove_friend(user_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    current_user = session[
        "user_id"
    ]


    if current_user == user_id:

        flash(
            "Invalid friend."
        )

        return redirect(
            url_for("friends")
        )


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor()


        user1 = min(
            current_user,
            user_id
        )

        user2 = max(
            current_user,
            user_id
        )


        cursor.execute(
            """
            DELETE FROM friendships

            WHERE
                user1_id = %s
                AND user2_id = %s
            """,
            (
                user1,
                user2
            )
        )


        db.commit()


        flash(
            "Friend removed successfully."
        )


    except Error as e:

        print(
            "Remove friend error:",
            e
        )

        if db:
            db.rollback()

        flash(
            "Could not remove friend."
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for("friends")
    )


# =========================================================
# CHAT
# =========================================================

@app.route(
    "/chat/<int:user_id>"
)
def chat(user_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    current_user = session[
        "user_id"
    ]


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET FRIEND
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                age,
                gender,
                city,
                profile_photo

            FROM users

            WHERE id = %s
            """,
            (
                user_id,
            )
        )


        friend = cursor.fetchone()


        if not friend:

            flash(
                "User not found."
            )

            return redirect(
                url_for("friends")
            )


        # -------------------------------------------------
        # CHECK FRIENDSHIP
        # -------------------------------------------------

        user1 = min(
            current_user,
            user_id
        )

        user2 = max(
            current_user,
            user_id
        )


        cursor.execute(
            """
            SELECT id
            FROM friendships

            WHERE
                user1_id = %s
                AND user2_id = %s
            """,
            (
                user1,
                user2
            )
        )


        friendship = cursor.fetchone()


        if not friendship:

            flash(
                "You can chat only with your friends."
            )

            return redirect(
                url_for("friends")
            )


        # -------------------------------------------------
        # GET MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT

                m.id,
                m.sender_id,
                m.receiver_id,
                m.message,
                m.created_at,

                u.name AS sender_name

            FROM messages m

            JOIN users u
                ON m.sender_id = u.id

            WHERE

                (
                    m.sender_id = %s
                    AND m.receiver_id = %s
                )

                OR

                (
                    m.sender_id = %s
                    AND m.receiver_id = %s
                )

            ORDER BY m.created_at ASC
            """,
            (
                current_user,
                user_id,
                user_id,
                current_user
            )
        )


        messages = cursor.fetchall()


        return render_template(
            "chat.html",
            friend=friend,
            messages=messages
        )


    except Error as e:

        print(
            "Chat error:",
            e
        )

        flash(
            "Could not load chat."
        )

        return redirect(
            url_for("friends")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# SEND MESSAGE
# =========================================================

@app.route(
    "/send-message/<int:user_id>",
    methods=["POST"]
)
def send_message(user_id):

    if not login_required():

        return redirect(
            url_for("login")
        )


    message = request.form.get(
        "message",
        ""
    ).strip()


    if not message:

        return redirect(
            url_for(
                "chat",
                user_id=user_id
            )
        )


    if len(message) > 2000:

        flash(
            "Message is too long."
        )

        return redirect(
            url_for(
                "chat",
                user_id=user_id
            )
        )


    current_user = session[
        "user_id"
    ]


    db = None
    cursor = None


    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # CHECK FRIENDSHIP
        # -------------------------------------------------

        user1 = min(
            current_user,
            user_id
        )

        user2 = max(
            current_user,
            user_id
        )


        cursor.execute(
            """
            SELECT id
            FROM friendships

            WHERE
                user1_id = %s
                AND user2_id = %s
            """,
            (
                user1,
                user2
            )
        )


        friendship = cursor.fetchone()


        if not friendship:

            flash(
                "You can message only your friends."
            )

            return redirect(
                url_for("friends")
            )


        # -------------------------------------------------
        # INSERT MESSAGE
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO messages
            (
                sender_id,
                receiver_id,
                message
            )

            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                current_user,
                user_id,
                message
            )
        )


        db.commit()


    except Error as e:

        print(
            "Send message error:",
            e
        )

        if db:
            db.rollback()

        flash(
            "Could not send message."
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for(
            "chat",
            user_id=user_id
        )
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>
        <a href="/">Go Home</a>
    </p>
    """, 404


# =========================================================
# 413 - FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "Profile image is too large. Maximum size is 5 MB."
    )

    return redirect(
        url_for("edit_profile")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )