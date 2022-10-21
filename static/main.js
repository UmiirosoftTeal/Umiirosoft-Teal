const tweetPush = document.getElementById('tweetPush');
const textCount = document.getElementById('textCount');

const tweetPushMB = document.getElementById('tweetPush-mb');
const textCountMB = document.getElementById('textCount-mb');

const Box = document.getElementById('Box');
const mbBox = document.getElementById('mbBox');



tweetPush.style.display = "none";
textCount.style.display = "none";

tweetPushMB.style.display = "none";
textCountMB.style.display = "none";


function ShowLength(str) {
    textCount.innerHTML = str.length + "文字 / 120文字";
    if (str.length <= 0) {
        tweetPush.style.display = "none";
        textCount.style.display = "none";
        tweetPush.disabled = true;
    }
    if (str.length >= 1) {
        tweetPush.style.display = "block";
        textCount.style.display = "block";
        tweetPush.disabled = false;
    }
    if (str.length > 120) {
        tweetPush.disabled = true;
        const over = 120 - str.length;
        textCount.innerHTML = "文字数制限 " + over + "文字";
    }
}

function ShowLengthMB(str) {
    textCountMB.innerHTML = str.length + "文字";
    if (str.length <= 0) {
        tweetPushMB.style.display = "none";
        textCountMB.style.display = "none";
        tweetPushMB.disabled = true;
    }
    if (str.length >= 1) {
        tweetPushMB.style.display = "block";
        textCountMB.style.display = "block";
        tweetPushMB.disabled = false;
    }
    if (str.length > 120) {
        tweetPushMB.disabled = true;
        const over = 120 - str.length;
        textCountMB.innerHTML = "文字数制限 " + over;
    }
}

function imgPreView(event) {
    var file = event.target.files[0];
    var reader = new FileReader();
    var preview = document.getElementById("preview");
    var previewImage = document.getElementById("previewImage");

    if (previewImage != null)
        preview.removeChild(previewImage);

    reader.onload = function (event) {
        var img = document.createElement("img");
        img.setAttribute("src", reader.result);
        img.setAttribute("id", "previewImage");
        preview.appendChild(img);

    };

    reader.readAsDataURL(file);
}

function imgPreViewMB(event) {
    var files = event.target.files[0];
    var readers = new FileReader();
    var previewMB = document.getElementById("preview-mb");
    var previewImages = document.getElementById("previewImages");

    if (previewImages != null)
        previewMB.removeChild(previewImages);

    readers.onload = function (event) {
        var imgs = document.createElement("img");
        imgs.setAttribute("src", readers.result);
        imgs.setAttribute("id", "previewImages");
        previewMB.appendChild(imgs);

    };
    readers.readAsDataURL(files);
}


var $grid = $('.page-content'),
    emptyCells = [],
    i;

// 子パネル (li.cell) の数だけ空の子パネル (li.cell.is-empty) を追加する。
for (i = 0; i < $grid.find('.tweet-item').length; i++) {
    emptyCells.push($('<div>', { class: 'tweet-item is-empty' }));
}

$grid.append(emptyCells);

var dialog = document.querySelector('dialog');
var showDialogButton = document.querySelector('#show-dialog');

if (!dialog.showModal) {
    dialogPolyfill.registerDialog(dialog);
}
showDialogButton.addEventListener('click', function () {
    dialog.showModal();
});
dialog.querySelector('.close').addEventListener('click', function () {
    dialog.close();
});