# Umiirosoft Teal | coding by @gamma_410
# Copyright 2022 Umiirosoft.

from importlib.metadata import requires
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
import datetime


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
    imgUrl = db.Column(db.Text)
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


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable=False)
    followUser = db.Column(db.String(20), nullable=False)

class FollowMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable=False)
    followUser = db.Column(db.String(20), nullable=False)


# S3 の設定
s3 = boto3.client('s3',
                  endpoint_url='https://object.gamma410.win:9000',
                  aws_access_key_id='minioadmin',
                  aws_secret_access_key='minioadmin'
                  )

# バケット名を代入しておく
Bucket = 'teal'


@app.route('/')
def redirect_func():
    return redirect('/home')


@app.route('/home', methods=['GET', 'POST'])
@login_required  # ログインチェック
def home():
    if request.method == 'GET':
        pwd = "見つける"
        tweets = Post.query.order_by(Post.id.desc()).all()
        return render_template('index.html', tweets=tweets, pwd=pwd)

    else:
        dt_now = datetime.datetime.now()
        postUser = current_user.username
        postTweet = request.form.get('postTweet')
        picture = request.files['imgUrl']
        postTweet = postTweet.replace('?', '？')
        postTweet = postTweet.replace('#', '＃')
        postTweet = postTweet.replace('\n', '__newLine__')
        tweetHex = postTweet.encode('utf-8')
        postTweetHex = tweetHex.hex()
        replyUser = None
        replyTweet = None
        replyTweetHex = None
        replyImgUrl = None
        dateY = dt_now.strftime("%Y")
        dateM = dt_now.strftime("%m")
        dateD = dt_now.strftime("%d")
        timeH = dt_now.strftime("%H")
        timeM = dt_now.strftime("%M")

        if picture:

            postTweetCode = postTweet.encode('utf-8')
            imgUrlHex = postTweetCode.hex()
            imgUrl = imgUrlHex + ".jpg"  # ファイル名

            iconMetaData = "image/jpeg"  # フォーマット指定

            # S3 アップロード
            s3.upload_fileobj(
                picture, Bucket, f'picture/{imgUrl}', ExtraArgs={'ContentType': iconMetaData})

            new_post = Post(postUser=postUser, postTweet=postTweet, postTweetHex=postTweetHex, imgUrl=imgUrl,
                            replyUser=replyUser, replyTweet=replyTweet, replyTweetHex=replyTweetHex, replyImgUrl=replyImgUrl,
                            dateY=dateY, dateM=dateM, dateD=dateD, timeH=timeH, timeM=timeM)

            db.session.add(new_post)
            db.session.commit()

        else:
            imgUrl = None
            new_post = Post(postUser=postUser, postTweet=postTweet, postTweetHex=postTweetHex, imgUrl=imgUrl,
                            replyUser=replyUser, replyTweet=replyTweet, replyTweetHex=replyTweetHex, replyImgUrl=replyImgUrl,
                            dateY=dateY, dateM=dateM, dateD=dateD, timeH=timeH, timeM=timeM)

            db.session.add(new_post)
            db.session.commit()

        return redirect('/home')


@app.route('/home/profile/<string:username>', methods=['GET', 'POST'])
def profile(username):
    post = Post.query.filter_by(
        postUser=username).order_by(Post.id.desc()).all()
    count = Post.query.filter_by(postUser=username).count()
    follow = Follow.query.filter_by(user=username).count()
    follower = Follow.query.filter_by(followUser=username).count()
    user = User.query.filter_by(username=username).first()
    followYou = Follow.query.filter_by(user=current_user.username).all()
    
    pwd = "プロフィール"
    return render_template("profile.html", username=username, post=post, user=user, count=count, follow=follow, follower=follower, followYou=followYou, pwd=pwd)


@app.route('/home/profile/edit_profile/<string:username>', methods=['GET', 'POST'])
def editProfile(username):
    pwd = "プロフィール編集"
    if request.method == "POST":
        try:
            usericon = request.files['userIcon']
            userdetail = request.form.get('postUserDetail')
            iconUrl = username + ".jpg"
            iconMetaData = "image/jpeg"  # フォーマット

            if usericon:
                s3.upload_fileobj(
                    usericon, Bucket, f'users/{iconUrl}', ExtraArgs={'ContentType': iconMetaData})
            else:
                print("パス")

            if userdetail:
                userData = User.query.filter_by(username=username).first()
                userData.userdetail = userdetail
                db.session.merge(userData)
                db.session.commit()

            else:
                print("パス")

            flash("プロフィールを変更しました！（WEBブラウザのキャッシュにより、すぐにアイコンが変更されない場合があります。）")
            return redirect(f'/home/profile/{ username }')

        except:
            flash("プロフィールの変更に失敗しました...")
            return redirect(f'/home/profile/{ username }')

    else:
        return render_template('editprof.html', pwd=pwd)


@app.route('/home/<string:username>/<string:tweet>/<string:tweethex>/<string:img>', methods=['GET', 'POST'])
def reply(username, tweet, tweethex, img):
    pwd = "投稿"
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
        tweet = tweet.replace('__newLine___', '\n')
        replyTweet = tweet
        replyTweetHex = tweethex
        dateY = dt_now.strftime("%Y")
        dateM = dt_now.strftime("%m")
        dateD = dt_now.strftime("%d")
        timeH = dt_now.strftime("%H")
        timeM = dt_now.strftime("%M")

        if img == "None":
            replyImgUrl = None
        else:
            replyImgUrl = img

        picture = request.files['imgUrl']

        postTweet = postTweet.replace('?', '？')

        if picture:

            postTweetCode = postTweet.encode('utf-8')
            imgUrlHex = postTweetCode.hex()
            imgUrl = imgUrlHex + ".jpg"  # ファイル名

            iconMetaData = "image/jpeg"  # フォーマット指定

            # S3 アップロード
            s3.upload_fileobj(
                picture, Bucket, f'picture/{imgUrl}', ExtraArgs={'ContentType': iconMetaData})

            new_post = Post(postUser=postUser, postTweet=postTweet, postTweetHex=postTweetHex, imgUrl=imgUrl,
                            replyUser=replyUser, replyTweet=replyTweet, replyTweetHex=replyTweetHex, replyImgUrl=replyImgUrl,
                            dateY=dateY, dateM=dateM, dateD=dateD, timeH=timeH, timeM=timeM)

            db.session.add(new_post)
            db.session.commit()

        else:
            imgUrl = None
            new_post = Post(postUser=postUser, postTweet=postTweet, postTweetHex=postTweetHex, imgUrl=imgUrl,
                            replyUser=replyUser, replyTweet=replyTweet, replyTweetHex=replyTweetHex, replyImgUrl=replyImgUrl,
                            dateY=dateY, dateM=dateM, dateD=dateD, timeH=timeH, timeM=timeM)

            db.session.add(new_post)
            db.session.commit()

        return redirect(f'/home/{ username }/{ tweet }/{ tweethex }/{ img }')

    else:
        post = Post.query.filter_by(
            postUser=username, postTweetHex=tweethex).first()
        reply = Post.query.filter_by(
            replyUser=username, replyTweetHex=tweethex).order_by(Post.id.desc()).all()
        return render_template('reply.html', post=post, reply=reply, pwd=pwd)


@app.route('/follow/list/<string:username>')
def follow(username):
    pwd = "フォロー中"
    user = username
    follow = Follow.query.filter_by(user=current_user.username).all()
    return render_template('follow.html', user=user, follow=follow, pwd=pwd)


@app.route('/follower/list/<string:username>')
def follower(username):
    pwd = "フォロワー"
    user = username
    follow = FollowMe.query.filter_by(user=current_user.username).all()
    return render_template('follower.html', user=user, follow=follow, pwd=pwd)


@app.route('/follow/add/<string:following>', methods=['GET', 'POST'])
def following(following):
    user = current_user.username
    followUser = following
    
    new_post = Follow(user=user, followUser=followUser)
    new_post2 = FollowMe(user=followUser, followUser=user)

    db.session.add(new_post)
    db.session.add(new_post2)
    db.session.commit()


    flash("フォローしました！")
    return redirect(f'/home/profile/{ current_user.username }')


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
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')

        else:
            flash("メールアドレスまたはパスワードが間違っています。<br>ご確認の上もう一度お試しください。")
            return redirect('/signin')

    else:
        return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        usericon = request.files['usericon']
        username = request.form.get('username')
        useremail = request.form.get('useremail')
        password = request.form.get('password')
        userdetail = "自己紹介を設定しよう！"

        if usericon:
            print("ok")
        else:
            flash("アイコン画像が設定されていません")
            return redirect('/signup')

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

        iconUrl = username + ".jpg"  # ファイル名
        iconMetaData = "image/jpeg"  # フォーマット指定

        # S3 アップロード
        s3.upload_fileobj(
            usericon, Bucket, f'users/{iconUrl}', ExtraArgs={'ContentType': iconMetaData})

        new_user = User(username=username, useremail=useremail, userdetail=userdetail,
                        password=generate_password_hash(password, method='sha256'))  # パスワードをハッシュ値に変換
        db.session.add(new_user)
        db.session.commit()

        flash("アカウント作成が完了しました！")

        return redirect('/signin')

    else:
        return render_template('signup.html')


@app.route('/logout')
@login_required  # ログインチェック
def logout():
    logout_user()
    return redirect('/about')

# ログイン前はリダイレクト


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/about')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
