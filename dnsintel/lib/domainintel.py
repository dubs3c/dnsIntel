from dnsintel.util.util import get_timestamp, dnsmasq, bind


class DomainIntel(object):
    """Class for representing a domain"""

    def __init__(self, the_domain, format_, type_, reference):
        self._domain = the_domain
        self._domain_formated = ""
        self._format = format_
        self._type = type_
        self._reference = reference
        self._created = get_timestamp()
        self._ALLOWED_FORMATS = ("DNSMASQ", "BIND")
        if self._format.upper() == "DNSMASQ":
            self._domain_formated = dnsmasq(self._domain)
        if self._format.upper() == "BIND":
            self._domain_formated = bind(self._domain)

    def __repr__(self):
        return f"domain: {self.domain}, domain_formated: {self.domain_formated}, \
        format: {self.format}, type: {self.type}, reference: {self.reference}, created: {self.created}"

    @property
    def domain(self) -> str:
        return self._domain

    @domain.setter
    def domain(self, value: str):
        self._domain = value

    @property
    def domain_formated(self):
        return self._domain_formated

    @domain_formated.setter
    def domain_formated(self, value):
        self._domain_formated = value

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value: str):
        if value.upper() == "DNSMASQ":
            self._domain_formated = dnsmasq(value)
        if value.upper() == "BIND":
            self._domain_formated = bind(value)
        self._format = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        self._created = value

