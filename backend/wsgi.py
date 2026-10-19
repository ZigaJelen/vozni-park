"""
Vstopna točka za Apache mod_wsgi.

mod_wsgi ob zagonu naloži to datoteko in poišče spremenljivko
z imenom `application`, ki ji nato posreduje vse HTTP zahteve.
"""
from app import create_app

application = create_app()