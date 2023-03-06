import urllib

class Config:
    IMAGE_SEARCH_URL = "https://tr.pinterest.com/resource/BaseSearchResource/get/?"
    def __init__(self, search_keywords="", file_lengths=100, image_quality="orig", bookmarks=""):
        self.search_keywords = search_keywords
        self.file_lengths = file_lengths
        self.image_quality = image_quality
        self.bookmarks = bookmarks

    #image search url
    @property
    def search_url(self):
        return self.IMAGE_SEARCH_URL

    #search parameter "source_url"
    @property
    def source_url(self):
         return "/search/pins/?q=" + urllib.parse.quote(self.search_keyword)

    #search parameter "data"
    @property
    def image_data(self):        
        if self.bookmarks == "":
            return '''{"options":{"isPrefetch":false,"query":"''' + self.search_keyword + '''","scope":"pins","no_fetch_context_on_resource":false},"context":{}}'''
        else:
            return '''{"options":{"page_size":25,"query":"''' + self.search_keyword + '''","scope":"pins","bookmarks":["''' + self.bookmark + '''"],"field_set_key":"unauth_react","no_fetch_context_on_resource":false},"context":{}}'''.strip()

    @property
    def search_keyword(self):
        return self.search_keywords
    
    @search_keyword.setter
    def search_keyword(self, search_keywords):
        self.search_keywords = search_keywords
    
    @property
    def file_length(self):
        return self.file_lengths
    
    @file_length.setter
    def file_length(self, file_lengths):
        self.file_lengths = file_lengths

    @property
    def image_quality(self):
        return self.image_qualitys
    
    @image_quality.setter
    def image_quality(self, image_qualitys):
        self.image_qualitys = image_qualitys

    @property
    def bookmark(self):
        return self.bookmarks

    @bookmark.setter
    def bookmark(self, bookmarks):
        self.bookmarks = bookmarks
    