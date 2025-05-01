from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Recreates the review table'

    def handle(self, *args, **options):
        sql = '''
        DROP TABLE IF EXISTS website_review;
        
        CREATE TABLE website_review (
            id CHAR(32) NOT NULL PRIMARY KEY,
            service VARCHAR(50) NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at DATETIME(6) NOT NULL,
            user_id CHAR(32) NOT NULL,
            CONSTRAINT website_review_user_service_unique UNIQUE (user_id, service),
            CONSTRAINT website_review_user_id_fk FOREIGN KEY (user_id) REFERENCES website_user (id) ON DELETE CASCADE
        );
        '''
        
        with connection.cursor() as cursor:
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        
        self.stdout.write(self.style.SUCCESS('Successfully recreated review table')) 