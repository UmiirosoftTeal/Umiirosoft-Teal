# Umiirosoft Teal | coding by @gamma_410
# Copyright 2022 Umiirosoft.


from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import hashlib

app = Flask(__name__)

# データベース作成 / 設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///postData.db'
app.config['SECRET_KEY'] = '5730292743938474948439320285857603'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tweetデータ
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postUser = db.Column(db.String(20), nullable=False)
    postTweet = db.Column(db.String(120), nullable=True)
    postTweetHex = db.Column(db.Text)
    imgUrl = db.Column(db.Text) # 廃止
    replyUser = db.Column(db.Text)
    replyTweet = db.Column(db.Text)
    replyTweetHex = db.Column(db.Text)
    replyImgUrl = db.Column(db.Text)
    dateY = db.Column(db.Text)
    dateM = db.Column(db.Text)
    dateD = db.Column(db.Text)
    timeH = db.Column(db.Text)
    timeM = db.Column(db.Text)
    RdateY = db.Column(db.Text)
    RdateM = db.Column(db.Text)
    RdateD = db.Column(db.Text)
    RtimeH = db.Column(db.Text)
    RtimeM = db.Column(db.Text)


# ログインデータ
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    userdetail = db.Column(db.Text)
    useremail = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)

@app.route('/')
def redirect_func():
    return redirect('/home')


@app.route('/home', methods=['GET', 'POST'])
@login_required  # ログインチェック
def home():
    if request.method == 'GET':
        pwd = "みつける"
        tweets = Post.query.order_by(Post.id.desc()).all()

        postUserLists = []
        replyPostUserLists = []
        for tweet in tweets:
            postUser = tweet.postUser
            user = User.query.filter_by(username=postUser).first()
            userEmail = user.useremail
            md5 = hashlib.md5(userEmail.encode("utf-8")).hexdigest()
            postUserLists.append(md5)

            replyPostUser = tweet.replyUser

            if replyPostUser == None:    
                nullMd5 = "null"
                replyPostUserLists.append(nullMd5)
            else:
                repUser = User.query.filter_by(username=replyPostUser).first()
                repUserEmail = repUser.useremail
                repMd5 = hashlib.md5(repUserEmail.encode("utf-8")).hexdigest()
                replyPostUserLists.append(repMd5)

        return render_template('index.html', pwd=pwd, l=zip(tweets, postUserLists, replyPostUserLists))

    else:
        dt_now = datetime.datetime.now()
        postUser = current_user.username
        postTweet = request.form.get('postTweet')
        postTweet = postTweet.replace('?', '？')
        postTweet = postTweet.replace('#', '＃')
        postTweet = postTweet.replace('\n', '__newLine__')
        tweetHex = postTweet.encode('utf-8')
        postTweetHex = tweetHex.hex()
        dateY = dt_now.strftime("%Y")
        dateM = dt_now.strftime("%m")
        dateD = dt_now.strftime("%d")
        timeH = dt_now.strftime("%H")
        timeM = dt_now.strftime("%M")        

        new_post = Post (
            postUser = postUser, 
            postTweet = postTweet, 
            postTweetHex = postTweetHex, 
            imgUrl = None,
            replyUser = None, 
            replyTweet = None, 
            replyTweetHex = None, 
            replyImgUrl = None,
            dateY = dateY, 
            dateM = dateM, 
            dateD = dateD, 
            timeH = timeH, 
            timeM = timeM
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect('/home')


@app.route('/<string:username>', methods=['GET', 'POST'])
def profile(username):
    post = Post.query.filter_by(postUser=username).order_by(Post.id.desc()).all()
    count = Post.query.filter_by(postUser=username).count()
    user = User.query.filter_by(username=username).first()
    email = user.useremail
    md5 = hashlib.md5(email.encode("utf-8")).hexdigest()

    pwd = "プロフィール"
    return render_template("profile.html", username=username, post=post, user=user, count=count, pwd=pwd, md5=md5)


@app.route('/edit_profile/<string:username>', methods=['GET', 'POST'])
def editProfile(username):
    pwd = "プロフィール編集"
    if request.method == "POST":
        if username == current_user.username:
            try:
                userdetail = request.form.get('postUserDetail')

                if userdetail:
                    userData = User.query.filter_by(username=username).first()
                    userData.userdetail = userdetail
                    db.session.merge(userData)
                    db.session.commit()

                else:
                    print("パス")

                flash("プロフィールを変更しました!")
                return redirect(f'/{ username }')

            except:
                flash("プロフィールの変更に失敗しました...")
                return redirect(f'/{ username }')
        else:
            flash("ログインしているアカウントが異なります...")
            return redirect(f'/{ username }')

    else:
        return render_template('editprof.html', pwd=pwd)


@app.route('/<string:username>/<string:tweethex>', methods=['GET', 'POST'])
def reply(username, tweethex):
    pwd = "くわしく"
    if request.method == 'POST':
        dt_now = datetime.datetime.now()
        postUser = current_user.username
        postTweet = request.form.get('postTweet')
        postTweet = postTweet.replace('?', '？')
        postTweet = postTweet.replace('#', '＃')
        postTweet = postTweet.replace('\n', '__newLine__')
        tweetHex = postTweet.encode('utf-8')
        postTweetHex = tweetHex.hex()
        replyUser = username

        tweet = bytes.fromhex(tweethex).decode("utf-8")

        tweet = tweet.replace('__newLine___', '\n')

        replyTweet = tweet
        replyTweetHex = tweethex
        dateY = dt_now.strftime("%Y")
        dateM = dt_now.strftime("%m")
        dateD = dt_now.strftime("%d")
        timeH = dt_now.strftime("%H")
        timeM = dt_now.strftime("%M")

        postTweet = postTweet.replace('?', '？')

        new_post = Post (
            postUser = postUser, 
            postTweet = postTweet, 
            postTweetHex = postTweetHex, 
            imgUrl = None,
            replyUser = replyUser, 
            replyTweet = replyTweet, 
            replyTweetHex = replyTweetHex, 
            replyImgUrl = None,
            dateY = dateY, 
            dateM = dateM, 
            dateD = dateD, 
            timeH = timeH, 
            timeM = timeM
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(f'/{ username }/{ tweethex }')

    else:
        post = Post.query.filter_by(postUser=username, postTweetHex=tweethex).first()
        postUser = User.query.filter_by(username=post.postUser).first()
        postUserEmail = postUser.useremail 
        md5 = hashlib.md5(postUserEmail.encode("utf-8")).hexdigest()
        
        if post.replyTweet:
            replyTweetUser = post.replyUser
            replyUser = User.query.filter_by(username=replyTweetUser).first()
            replyTweetUserMd5 = hashlib.md5(replyUser.useremail.encode("utf-8")).hexdigest()
        else:
            replyTweetUserMd5 = None

        replys = Post.query.filter_by(replyUser=username, replyTweetHex=tweethex).order_by(Post.id.desc()).all()

        replyUserNames = []
        for reply in replys:
            replyUser = reply.postUser

            if replyUser:
                replyUserEmailSetup = User.query.filter_by(username=replyUser).first()
                replyUserEmail = replyUserEmailSetup.useremail
                replyUserMd5 = hashlib.md5(replyUserEmail.encode("utf-8")).hexdigest()
                replyUserNames.append(replyUserMd5)

        return render_template('reply.html', post=post, l=zip(replys, replyUserNames), pwd=pwd, md5=md5, replyTweetUserMd5=replyTweetUserMd5)


# ログイン前系統
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        useremail = request.form.get('useremail')
        password = request.form.get('password')

        if useremail:
            print("ok")
        else:
            flash("メールアドレスが入力されていません")
            return redirect('/signin')

        if password:
            print("ok")
        else:
            flash("パスワードが入力されていません")
            return redirect('/signin')

        # Userテーブルからusernameに一致するユーザを取得
        user = User.query.filter_by(useremail=useremail).first()

        if user:
            print("ok")
        else:
            flash("メールアドレスまたはパスワードが間違っています。<br>ご確認の上もう一度お試しください。")
            return redirect('/signin')

        if check_password_hash(user.password, password):
            try:
                login_user(user)
                return redirect('/home')
            except:
                flash("メールアドレスまたはパスワードが間違っています。<br>ご確認の上もう一度お試しください。")
                return redirect('/signin')

        else:
            flash("メールアドレスまたはパスワードが間違っています。<br>ご確認の上もう一度お試しください。")
            return redirect('/signin')

    else:
        return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        useremail = request.form.get('useremail')
        password = request.form.get('password')
        userdetail = "自己紹介を設定しよう！"

        if username:
            print("ok")
        else:
            flash("ユーザー名が設定されていません")
            return redirect('/signup')

        if useremail:
            print("ok")
        else:
            flash("メールアドレスが設定されていません")
            return redirect('/signup')

        if password:
            print("ok")
        else:
            flash("パスワードが設定されていません")
            return redirect('/signup')

        userData = User.query.filter_by(username=username).first()

        if userData == None:
            print("ok")
        else:
            flash("同じ名前のユーザーが既に存在しています")
            return redirect('/signup')

        new_user = User(username=username, useremail=useremail, userdetail=userdetail,
                        password=generate_password_hash(password, method='sha256'))  # パスワードをハッシュ値に変換
        db.session.add(new_user)
        db.session.commit()

        flash("アカウント作成が完了しました！")

        return redirect('/signin')

    else:
        return render_template('signup.html')


@app.route('/dev')
@login_required
def dev():
    if current_user.username == "gamma":
        posts = Post.query.order_by(Post.id.desc()).all()
        users = User.query.order_by(User.id.desc()).all()
        md5Lists = []
        for user in users:
            email = user.useremail
            md5 = hashlib.md5(email.encode("utf-8")).hexdigest()
            md5Lists.append(md5)

        return render_template("dev.html", posts=posts, l=zip(users, md5Lists))

    else:
        return "404"

@app.route('/del/<string:u>/<int:n>')
@login_required
def tweetDelete(u, n):
    if u == current_user.username:
        post = Post.query.filter_by(id=n).first()
        db.session.delete(post)
        db.session.commit()
        flash("つぶやきを削除しました !")
        return redirect(f'/{ u }')
    else:
        flash("ログインしているアカウントが異なります...")
        return redirect(f'/{ u }')


@app.route('/dev/deleteTweet/<int:n>')
@login_required
def devTweetDelete(n):
    post = Post.query.filter_by(id=n).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/dev')


@app.route('/dev/deleteUser/<int:n>')
@login_required
def devUserDelete(n):
    user = User.query.filter_by(id=n).first()
    db.session.delete(user)
    db.session.commit()
    return redirect('/dev')


@app.route('/logout')
@login_required  # ログインチェック
def logout():
    logout_user()
    return redirect('/about')


# ログイン前はリダイレクト
@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/about')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)