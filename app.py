# Umiirosoft Teal | coding by @gamma_410
# Copyright 2022 Umiirosoft.

from importlib.metadata import requires
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import boto3

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
    postTweet = db.Column(db.String(280), nullable=True)
    replyUser = db.Column(db.Text)
    replyTweet = db.Column(db.Text)
    imgUrl = db.Column(db.Text)

# ログインデータ


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    userdetail = db.Column(db.Text)
    useremail = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)


# S3 の設定
s3 = boto3.client('s3',
                  endpoint_url='https://object.gamma410.win',
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
        tweets = Post.query.order_by(Post.id.desc()).all()
        return render_template('index.html', tweets=tweets)

    else:
        postUser = current_user.username
        postTweet = request.form.get('postTweet')
        picture = request.files['imgUrl']
        postTweet = postTweet.replace('?', '？')
        replyUser = None
        replyTweet = None
        if picture:

            postTweetCode = postTweet.encode('utf-8')
            imgUrlHex = postTweetCode.hex()
            imgUrl = imgUrlHex + ".jpg"  # ファイル名

            iconMetaData = "image/jpeg"  # フォーマット指定

            # S3 アップロード
            s3.upload_fileobj(
                picture, Bucket, f'picture/{imgUrl}', ExtraArgs={'ContentType': iconMetaData})

            new_post = Post(postUser=postUser, postTweet=postTweet,
                            replyUser=replyUser, replyTweet=replyTweet, imgUrl=imgUrl)

            db.session.add(new_post)
            db.session.commit()

        else:
            imgUrl = None
            new_post = Post(postUser=postUser, postTweet=postTweet,
                            replyUser=replyUser, replyTweet=replyTweet, imgUrl=imgUrl)

            db.session.add(new_post)
            db.session.commit()

        return redirect('/home')

@app.route('/home/profile/<string:username>', methods=['GET', 'POST'])
def profile(username):
    post = Post.query.filter_by(postUser=username).order_by(Post.id.desc()).all()
    count = Post.query.filter_by(postUser=username).count()
    user = User.query.filter_by(username=username).first()
    return render_template("profile.html", username=username, post=post, user=user, count=count)


@app.route('/home/profile/edit_profile/<string:username>', methods=['GET', 'POST'])
def editProfile(username):
    if request.method == "POST":
        try:
            usericon = request.files['userIcon']
            userdetail = request.form.get('postUserDetail')
            iconUrl = username + ".jpg"
            iconMetaData = "image/jpeg"  # フォーマット

            if usericon:
                s3.upload_fileobj(usericon, Bucket, f'users/{iconUrl}', ExtraArgs={'ContentType': iconMetaData})
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
        return render_template('editprof.html')


@app.route('/home/<string:username>/<string:tweet>', methods=['GET', 'POST'])
def reply(username, tweet):
    if request.method == 'POST':
        postUser = current_user.username
        postTweet = request.form.get('postTweet')
        replyUser = username
        replyTweet = tweet
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

            new_post = Post(postUser=postUser, postTweet=postTweet,
                            replyUser=replyUser, replyTweet=replyTweet, imgUrl=imgUrl)

            db.session.add(new_post)
            db.session.commit()

        else:
            imgUrl = None
            new_post = Post(postUser=postUser, postTweet=postTweet,
                            replyUser=replyUser, replyTweet=replyTweet, imgUrl=imgUrl)

            db.session.add(new_post)
            db.session.commit()

        return redirect(f'/home/{ username }/{ tweet }')

    else:
        post = Post.query.filter_by(postUser=username, postTweet=tweet).first()
        reply = Post.query.filter_by(replyUser=username, replyTweet=tweet).order_by(Post.id.desc()).all()
        return render_template('reply.html', post=post, reply=reply)


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
