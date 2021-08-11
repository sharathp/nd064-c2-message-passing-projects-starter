def register_routes(api, app, root="person-api"):
    from app.udaconnect import register_routes as attach_udaconnect

    # Add routes
    attach_udaconnect(api, app)
