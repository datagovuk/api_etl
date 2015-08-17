import psycopg2

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
        import csv; reader = csv.reader(open(input_file))
        q = self._create_sql(service_manifest, reader.next())

        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()


    def load_data(self, service_manifest, source_file):
        print "  Loading data into table {}".format(service_manifest.name)



    def _create_sql(self, service_manifest, headers):
        # TODO: We should here check the schema for required fields so can can NOT NULL
        # the relevant columns - making sure to slugify them first ...
        columns = []

        table_settings = service_manifest.table_settings

        pkname =table_settings['pk_name']

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
            s = "CREATE INDEX ON {} ((lower({})))".format(service_manifest.name, i)
            idx.append(s)

        idx = ";\n".join(idx)

        return q + idx



