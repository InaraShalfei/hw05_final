from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об авторе'
        context['header'] = 'Об авторе проекта'
        context['simple_text'] = 'Hey everyone! My name is Inara!'
        context['main_text'] = 'Hey everyone! My name is Inara,' \
                               ' and I am an English and Russian online teacher!'

        return context


class AboutTechView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Технологии'
        context['header'] = 'О технологиях проекта'
        context['simple_text'] = 'Этот проект с содержательным описанием написан на Python'
        context['main_text'] = 'Этот проект с содержательным описанием написан на Python,' \
                               'с использование фреймворка Django.' \
                               'Все методы протестированы.'

        return context
