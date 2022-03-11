import re

from django.utils.deprecation import MiddlewareMixin

from django_mobile import _init_flavour, flavour_storage, set_flavour
from django_mobile.conf import settings


class SetFlavourMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _init_flavour(request)

        if settings.FLAVOURS_GET_PARAMETER in request.GET:
            flavour = request.GET[settings.FLAVOURS_GET_PARAMETER]
            if flavour in settings.FLAVOURS:
                set_flavour(flavour, request, permanent=True)

    def process_response(self, request, response):
        flavour_storage.save(request, response)
        return response


class MobileDetectionMiddleware(MiddlewareMixin):
    user_agents_test_match = (
        "w3c ",
        "acs-",
        "alav",
        "alca",
        "amoi",
        "audi",
        "avan",
        "benq",
        "bird",
        "blac",
        "blaz",
        "brew",
        "cell",
        "cldc",
        "cmd-",
        "dang",
        "doco",
        "eric",
        "hipt",
        "inno",
        "ipaq",
        "java",
        "jigs",
        "kddi",
        "keji",
        "leno",
        "lg-c",
        "lg-d",
        "lg-g",
        "lge-",
        "maui",
        "maxo",
        "midp",
        "mits",
        "mmef",
        "mobi",
        "mot-",
        "moto",
        "mwbp",
        "nec-",
        "newt",
        "noki",
        "xda",
        "palm",
        "pana",
        "pant",
        "phil",
        "play",
        "port",
        "prox",
        "qwap",
        "sage",
        "sams",
        "sany",
        "sch-",
        "sec-",
        "send",
        "seri",
        "sgh-",
        "shar",
        "sie-",
        "siem",
        "smal",
        "smar",
        "sony",
        "sph-",
        "symb",
        "t-mo",
        "teli",
        "tim-",
        "tosh",
        "tsm-",
        "upg1",
        "upsi",
        "vk-v",
        "voda",
        "wap-",
        "wapa",
        "wapi",
        "wapp",
        "wapr",
        "webc",
        "winw",
        "xda-",
    )
    user_agents_test_search = "(?:%s)" % "|".join(
        (
            "up.browser",
            "up.link",
            "mmp",
            "symbian",
            "smartphone",
            "midp",
            "wap",
            "phone",
            "windows ce",
            "pda",
            "mobile",
            "mini",
            "palm",
            "netfront",
            "opera mobi",
        )
    )
    user_agents_exception_search = "(?:%s)" % "|".join(("ipad",))
    http_accept_regex = re.compile("application/vnd\.wap\.xhtml\+xml", re.IGNORECASE)

    def __init__(self):
        super().__init__()
        user_agents_test_match = r"^(?:%s)" % "|".join(self.user_agents_test_match)
        self.user_agents_test_match_regex = re.compile(
            user_agents_test_match, re.IGNORECASE
        )
        self.user_agents_test_search_regex = re.compile(
            self.user_agents_test_search, re.IGNORECASE
        )
        self.user_agents_exception_search_regex = re.compile(
            self.user_agents_exception_search, re.IGNORECASE
        )

    def process_request(self, request):
        is_mobile = False

        if "HTTP_USER_AGENT" in request.META:
            user_agent = request.META["HTTP_USER_AGENT"]

            # Test common mobile values.
            if self.user_agents_test_search_regex.search(
                user_agent
            ) and not self.user_agents_exception_search_regex.search(user_agent):
                is_mobile = True
            else:
                # Nokia like test for WAP browsers.
                # http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

                if "HTTP_ACCEPT" in request.META:
                    http_accept = request.META["HTTP_ACCEPT"]
                    if self.http_accept_regex.search(http_accept):
                        is_mobile = True

            if not is_mobile:
                # Now we test the user_agent from a big list.
                if self.user_agents_test_match_regex.match(user_agent):
                    is_mobile = True

        if is_mobile:
            set_flavour(settings.DEFAULT_MOBILE_FLAVOUR, request)
        else:
            set_flavour(settings.FLAVOURS[0], request)
