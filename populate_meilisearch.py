from bibliomar_helper.populate_meili.populate import populate_meilisearch

# Add relevant fields from the database to the main Meilisearch index in batches of 100.
if __name__ == "__main__":
    populate_meilisearch("fiction")
    populate_meilisearch("scitech")
