import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limitless.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Drop the existing table
    cursor.execute('DROP TABLE IF EXISTS website_review;')
    
    # Create the new table
    cursor.execute('''
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
    ''')
    
    print("Successfully recreated review table") 