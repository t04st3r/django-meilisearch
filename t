[1mdiff --git a/.env.example b/.env.example[m
[1mindex 6030ee0..6d11d1f 100644[m
[1m--- a/.env.example[m
[1m+++ b/.env.example[m
[36m@@ -15,7 +15,7 @@[m [mPOSTGRES_PORT=5432[m
 REDIS_URL=redis://redis:6379/0[m
 [m
 #meilisearch[m
[31m-MEILI_URL=http://localhost:7700[m
[32m+[m[32mMEILI_URL=http://meilisearch:7700[m
 MEILI_ENV=production[m
 MEILI_LOG_LEVEL=debug[m
 MEILI_NO_ANALYTICS=true[m
[1mdiff --git a/django_meilisearch/settings.py b/django_meilisearch/settings.py[m
[1mindex 1c1ca66..da638a0 100644[m
[1m--- a/django_meilisearch/settings.py[m
[1m+++ b/django_meilisearch/settings.py[m
[36m@@ -73,6 +73,10 @@[m [mTEMPLATES = [[m
     },[m
 ][m
 [m
[32m+[m[32mMEILISEARCH_URL = environ.get("MEILI_URL", "http://localhost:7700")[m
[32m+[m[32mMEILISEARCH_API_KEY = environ.get("MEILI_MASTER_KEY", "supersecretlongkey")[m
[32m+[m
[32m+[m
 WSGI_APPLICATION = "django_meilisearch.wsgi.application"[m
 [m
 REST_FRAMEWORK = {[m
