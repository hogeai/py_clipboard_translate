# coding=utf-8
import pyperclip, re, threading
import webbrowser, urllib.parse
from normalize_neologd import Preprocessing

TRANCELATE_URL = 'https://translate.google.com/?source=gtx#view=home&op=translate&sl=auto&tl=ja&text='
pre_copy_text = ""
p = Preprocessing()


def esc_paper(text):
    text = re.sub(r'^ +', '', text)
    m = re.search(r"^http", text)
    if m:
        return False

    text = re.sub(r'[-  0-9、。・]', '', text)
    if len(text) < 2:
        return False

    return True


def text_format(text):
    # 論文の折り返し部分に対応
    new = re.sub(r'-[\r\n]', '', text)
    new = re.sub(r'^-', ' ', new)
    new = re.sub(r'[\r\n]', ' ', new)
    new = re.sub(r'[/ 　;:]', ' ', new)
    # できるだけ感覚に近い翻訳になるように頑張る
    new = re.sub(r'([ a-zA-Z0-9(])\. ?([a-z0-9)])', '\\1-_-\\2', new)
    new = p.normalize_neologd(new)
    lines = [re.sub(r'-_-', '.', line) for line in new.split('.')]
    return lines


def check_jp(text):
    # 「あ～ん」
    match = re.search(r'[\u3041-\u3093\u30a1-\u30fc\u4e00-\u9fa5]', text)
    if match:
        return False
    return True


def check_translate():
    global pre_copy_text

    copy_text = str(pyperclip.paste())
    if len(copy_text) > 0:
        # コピー後放置するパターンを考慮
        if pre_copy_text[:10] != copy_text[:10]:
            # 日本語の場合処理しない
            if check_jp(copy_text):
                # エスケープしたいか？
                if esc_paper(copy_text):
                    # 前処理
                    new_text_lines = text_format(copy_text)
                    if len(new_text_lines) > 0:
                        # 前回と同じコピーか？
                        if pre_copy_text != new_text_lines[0]:
                            pre_copy_text = new_text_lines[0]
                            mod_text = ".\r\n".join(new_text_lines)
                            # 前処理済みの内容をクリップボードに入れておく
                            pyperclip.copy(mod_text)
                            print("-" * 20, "change clip", "-" * 20)
                            # google翻訳
                            webbrowser.open(TRANCELATE_URL + urllib.parse.quote(mod_text))

    th = threading.Timer(5, check_translate)
    th.start()


def main():
    t = threading.Thread(target=check_translate)
    t.start()


if __name__ == "__main__":
    main()
