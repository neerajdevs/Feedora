class DatabaseRouter:

    # Mongo models app name
    route_app_labels = {"ContentModule"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "mongo"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "mongo"
        return "default"

    def allow_migrate(self, db, app_label, **hints):
        if app_label in self.route_app_labels:
            return db == "mongo"
        return db == "default"