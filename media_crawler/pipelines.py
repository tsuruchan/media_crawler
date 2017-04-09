# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
import psycopg2.extras
from scrapy.exceptions import DropItem
from datetime import datetime, timedelta


class ValidationPipeline(object):
    """
    Itemを検証するPipeline
    """
    def process_item(self, item, spider):
        if not item['title']:
            # titleが取得出来てないときにエラーを表示
            raise DropItem('Missing title')

        return item


class DatabasePipeline(object):
    """
    ItemをPostgreSQLに保存するPipeline
    """
    def open_spider(self, spider):
        """
        Spidefの開始時にPostgreSQLサーバーに接続する
        """

        # PostgreSQLサーバーへ接続
        try:
            self.c = psycopg2.connect('host=localhost dbname=big_data_sql user=postgres')
        except:
            print("Connection Error")

        # 自動コミットをオン
        self.c.autocommit = True

        # 列名でアクセスする（item['name']の形でアクセス）
        self.cur = self.c.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # gunosyテーブルの定義
        self.cur.execute('create table if not exists gunosy (title text, url text, tag text, date timestamp, publisher text, images text, top_image text, body text)')

    def process_item(self, item, spider):
        """
        itemをitemsテーブルに挿入する
        """
        # DBに保存されている最新の記事の時間を取得
        self.cur.execute('select date from gunosy order by date desc')

        # 最新の記事があったら取得してDBに入れる
        if self.cur.fetchone()[0] < datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S+09:00'):

            # URLの重複チェック
            self.cur.execute('select url from gunosy where url = (%s)', [item['url']])
            if self.cur.fetchone() is None:
                print("★★★★ insert SQL")
                self.cur.execute('insert into gunosy values (%s, %s, %s, %s, %s, %s, %s, %s)',
                                 [item["title"], item["url"], item["tag"], item["date"], item["publisher"],
                                  ','.join(item["images"]), item["top_image"], item["body"]])
            else:
                print("★★★★ 重複だよ！!")
                pass
        else:
            print("★★★★ 重複だよ！")
            pass

    def close_spider(self, spider):
        """
        Spiderの終了時にPostgreSQLサーバーへの接続を切断する
        """
        self.c.close()
        self.cur.close()
