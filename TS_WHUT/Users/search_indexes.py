from haystack import indexes
from .models import ImageModel

class ImageModelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, using_tamplate=True)

    def get_model(self):
        return ImageModel

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
