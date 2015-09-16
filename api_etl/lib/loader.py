import psycopg2
import unicodecsv as csv

class Loader(object):
    """
    Is capable of loading the provided CSV file, and hopefully determining
    what is new data and what isn't.  Will also create the table for the
    service if it does not exist.
    """
    def init_connection(self, db):
        self.database_name = db

    def close_connection(self):
        pass

    def table_exists(self, service_manifest):
        return False


    def create_table(self, service_manifest, input_file):
        pass

    def load_data(self, source_file):
        pass

class PostgresLoader(Loader):
    """

    """
    def init_connection(self, db):
        from api_etl.config import Config
        self.config = Config()

        self.database_name = db
        owner = self.config.database('owner')
        self.conn = psycopg2.connect("dbname={} user={}".format(db, owner))

    def close_connection(self):
        self.conn.close()

    def table_exists(self, service_manifest):
        print "  Checking if table {} exists in DB {}".format(service_manifest.name, self.database_name)
        q = """
            SELECT EXISTS (
               SELECT 1
               FROM   information_schema.tables
               WHERE  table_schema = 'public'
               AND    table_name = '{}'
            );
        """.strip().format(service_manifest.name)

        cur = self.conn.cursor()
        cur.execute(q)
        result = cur.fetchone()
        cur.close()

        return result[0]

    def create_table(self, service_manifest, input_file):
        print "  Creating table {} in DB {}".format(service_manifest.name, self.database_name)
        reader = csv.reader(open(input_file))
        q = self._create_sql(service_manifest, reader.next())

        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def load_data(self, service_manifest, source_file, encoding):
        pk = service_manifest.table_settings["pk_name"]

        print "  Loading data into table {}".format(service_manifest.name)
        reader = csv.DictReader(open(source_file), encoding=encoding)
        inserted = 0
        for row in reader:
            print row
            if not self._row_exists(row[pk], pk, service_manifest.name):
                self._insert_row(service_manifest.name, row)
                inserted += 1

        if inserted:
            self.conn.commit()

        print "  Inserted {} rows into database".format(inserted)

    def _insert_row(self, tablename, row):
        cols = []
        vals = []

        cols = [k for k in row.keys()]
        for c in cols:
            v = row[c].replace("'", "''")
            vals.append(u"'{}'".format(v).strip())

        cols = ",".join(cols)
        vals = ','.join(vals)
        q = u"""
            INSERT INTO {tbl}({cols})
            VALUES({vals});
        """.format(tbl=tablename, cols=cols, vals=vals).strip()

        cur = self.conn.cursor()
        cur.execute(q)
        cur.close()


    def _row_exists(self, id, column, tablename):
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM {tbl} WHERE {col}='{val}'".format(tbl=tablename, col=column, val=id))
        result = cur.fetchone()
        cur.close()

        return result[0]

    def _get_pk_name(self, service_manifest):
        table_settings = service_manifest.table_settings
        return table_settings['pk_name']

    def _create_sql(self, service_manifest, headers):
        # TODO: We should here check the schema for required fields so can can NOT NULL
        # the relevant columns - making sure to slugify them first ...
        columns = []

        pkname = self._get_pk_name(service_manifest)

        table_settings = service_manifest.table_settings
        indices = [i.strip() for i in table_settings['index'].split(',')]
        print "  Indices are {}".format(indices)

        for h in headers:
            if pkname and pkname == h:
                columns.append("{} TEXT primary key".format(h))
            else:
                columns.append("{} TEXT".format(h))

        q = """
            CREATE TABLE {}({});\n
        """.strip().format(service_manifest.name, ",\n".join(columns))
        idx = []
        for i in indices:
            s = "CREATE INDEX ON {} ((lower({})));".format(service_manifest.name, i)
            idx.append(s)

        idx = ";\n".join(idx)

        grant_q = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(self.config.database('reader_username'))

        return q + idx + grant_q



