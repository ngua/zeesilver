import shutil
import tarfile
import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from common.utils import cd


class Command(BaseCommand):
    """
    Management command to fetch and extract GeoIP2 databases in tar.gz format
    from URL specified in settings
    Intended primarily to be run as monthly celerybeat task
    """
    help = 'Downloads and extracts most recent GeoIP2 database archives'

    def __init__(self):
        self.geoip_path = getattr(settings, 'GEOIP_PATH', '/geoip2')
        self.geoip_country = getattr(settings, 'GEOIP_COUNTRY', 'country.mmdb')
        self.geoip_city = getattr(settings, 'GEOIP_CITY', 'city.mmdb')
        self.databases = {
            self.geoip_country: settings.GEODB_COUNTRY_PERMALINK,
            self.geoip_city: settings.GEODB_CITY_PERMALINK,
        }

    def handle(self, *args, **kwargs):
        # Ensure that URLs are defined in settings module
        if any(url is None for url in self.databases.values()):
            raise CommandError(
                'Please configure GeoIP URLs in settings module'
            )

        # Use custom context manager to cd into db path specified in
        # settings. This is somewhat easier than calling os.path.join
        # to ensure the correct path
        with cd(self.geoip_path):
            for db_name, url in self.databases.items():
                self.fetch_archives(db_name, url)

    def fetch_archives(self, db_name, url):
        """
        Downloads the latest database archives from the GeoIP2 provider.
        Because the requests library automatically decompresses tgz archives,
        the byte stream returned from the URL is written to a new file to be
        decompressed and extracted by the `extract_archive` method below
        """
        archive_name = f'{db_name}.tgz'
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
        except requests.HTTPError as e:
            raise CommandError(e)
        with open(archive_name, 'wb') as archive:
            archive.write(response.raw.read())
        self.extract_archive(archive_name, db_name)

    def extract_archive(self, archive_name, db_name):
        """
        Extracts the .mmdb file from the newly created tgz by iterating through
        the archive and matching against the correct file extension. Because
        of how MM archives it dbs, the db file will be placed in an
        intervening directory.  Rather then extract it and then move it to
        the `geoip_path` specified in the settings, this method writes the file
        contents directly to the specified filepath
        """
        try:
            with tarfile.open(archive_name, 'r:gz') as archive:
                for file in archive:
                    if file.name.endswith('mmdb'):
                        file_obj = archive.extractfile(file)
                        try:
                            with open(db_name, 'wb') as db_file:
                                shutil.copyfileobj(file_obj, db_file)
                        except shutil.Error as e:
                            raise CommandError(e)
                        break
        except tarfile.TarError as e:
            raise CommandError(e)
