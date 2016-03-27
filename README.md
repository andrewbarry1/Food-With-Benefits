Food With Benefits
==================

An extensive customer loyalty program, and administration website. Supports multiple individual and separate stores, multiple customer offers based on a "channels" system, decentralization of customer data, a highly customizable mass-messaging system, custom app branding, and other wonderful features.

Requirements:

	* Python 2.7
	  1. Sendgrid
	  2. Plivo
	  3. Pbkdf2
	  4. Psycopg2
	  5. Web.py
	* Apache 2
	* Postgresql

The database can be set up using the script in *api/scripts/createdb.py*, the rest is up to you to figure out. Most of the installation work will involve configuring Apache, setting a few env vars, and removing the reliance on an old domain. Regardless, the security of this website cannot be guaranteed, so use at your own risk.

**TODO:** Add the POS app for iOS xcode project
