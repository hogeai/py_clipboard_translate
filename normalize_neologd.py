# coding＝utf-8
# https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp

from __future__ import unicode_literals
import re
import unicodedata


class Preprocessing:
    def __init__(self):
        pass

    def unicode_normalize(self, cls, s):
        pt = re.compile('([{}]+)'.format(cls))

        def norm(c):
            return unicodedata.normalize('NFKC', c) if pt.match(c) else c

        s = ''.join(norm(x) for x in re.split(pt, s))
        s = re.sub('－', '-', s)
        return s

    def remove_extra_spaces(self, s):
        s = re.sub('[ 　]+', ' ', s)
        blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                          '\u3040-\u309F',  # HIRAGANA
                          '\u30A0-\u30FF',  # KATAKANA
                          '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                          '\uFF00-\uFFEF'  # HALFWIDTH AND FULLWIDTH FORMS
                          ))
        basic_latin = '\u0000-\u007F'

        def remove_space_between(cls1, cls2, s):
            p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
            while p.search(s):
                s = p.sub(r'\1\2', s)
            return s

        s = remove_space_between(blocks, blocks, s)
        s = remove_space_between(blocks, basic_latin, s)
        s = remove_space_between(basic_latin, blocks, s)
        return s

    def normalize_neologd(self, s):
        s = s.strip()
        s = self.unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)

        def maketrans(f, t):
            return {ord(x): ord(y) for x, y in zip(f, t)}

        s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
        s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
        s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
        s = s.translate(
            maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
                      '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))

        s = self.remove_extra_spaces(s)
        s = self.unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
        s = re.sub('[’]', '\'', s)
        s = re.sub('[”]', '"', s)
        return s


if __name__ == "__main__":
    p = Preprocessing()
    assert "0123456789" == p.normalize_neologd("０１２３４５６７８９")
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" == p.normalize_neologd("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ")
    assert "abcdefghijklmnopqrstuvwxyz" == p.normalize_neologd("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")
    assert "!\"#$%&'()*+,-./:;<>?@[¥]^_`{|}" == p.normalize_neologd("！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝")
    assert "＝。、・「」" == p.normalize_neologd("＝。、・「」")
    assert "ハンカク" == p.normalize_neologd("ﾊﾝｶｸ")
    assert "o-o" == p.normalize_neologd("o₋o")
    assert "majikaー" == p.normalize_neologd("majika━")
    assert "わい" == p.normalize_neologd("わ〰い")
    assert "スーパー" == p.normalize_neologd("スーパーーーー")
    assert "!#" == p.normalize_neologd("!#")
    assert "ゼンカクスペース" == p.normalize_neologd("ゼンカク　スペース")
    assert "おお" == p.normalize_neologd("お             お")
    assert "おお" == p.normalize_neologd("      おお")
    assert "おお" == p.normalize_neologd("おお      ")
    assert "検索エンジン自作入門を買いました!!!" == \
           p.normalize_neologd("検索 エンジン 自作 入門 を 買い ました!!!")
    assert "アルゴリズムC" == p.normalize_neologd("アルゴリズム C")
    assert "PRML副読本" == p.normalize_neologd("　　　ＰＲＭＬ　　副　読　本　　　")
    assert "Coding the Matrix" == p.normalize_neologd("Coding the Matrix")
    assert "南アルプスの天然水Sparking Lemonレモン一絞り" == \
           p.normalize_neologd("南アルプスの　天然水　Ｓｐａｒｋｉｎｇ　Ｌｅｍｏｎ　レモン一絞り")
    assert "南アルプスの天然水-Sparking*Lemon+レモン一絞り" == \
           p.normalize_neologd("南アルプスの　天然水-　Ｓｐａｒｋｉｎｇ*　Ｌｅｍｏｎ+　レモン一絞り")
