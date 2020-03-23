import bs4
import genanki


DECK_ID = 1552031589
NOUN_MODULE_ID = 1932299662
NON_NOUN_MODULE_ID = 1815325576

COLOR_NEUTER = '#35a541'
COLOR_FEMININE = '#c271c2'
COLOR_MASCULINE = '#5271c2'

ARTICLE_NEUTER = 'das'
ARTICLE_FEMININE = 'die'
ARTICLE_MASCULINE = 'der'

ARTICLES = ARTICLE_NEUTER, ARTICLE_FEMININE, ARTICLE_MASCULINE

CSS = '''
.card {
    font-family: arial;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    color: black;
    background-color: white;
}
'''

NOUN_CSS = CSS + '''
.plural {
    color: black;
    font-size: 70%;
    font-weight: normal;
    font-style: italic;
}

.plural::before {
    content: "pl. ";
    color: gray;
}
'''

simple_model = genanki.Model(
    NON_NOUN_MODULE_ID,
    'Simple Model',
    fields=[
        {'name': 'Word'},
        {'name': 'Translation'},
    ],
    css=CSS,
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Word}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Translation}}',
        },
        {
            'name': 'Card 2',
            'qfmt': '{{Translation}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Word}}',
        },
    ]
)

non_noun_model = simple_model
noun_without_plurals_model = simple_model

noun_with_plurals_model = genanki.Model(
    NOUN_MODULE_ID,
    'Model With Plurals',
    fields=[
        {'name': 'Singular'},
        {'name': 'Plural'},
        {'name': 'Translation'},
    ],
    css=NOUN_CSS,
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Singular}}<br><span class="plural">{{Plural}}</span>',
            'afmt': '{{FrontSide}}<hr id="answer">{{Translation}}',
        },
        {
            'name': 'Card 2',
            'qfmt': '{{Translation}}',
            'afmt': (
                '{{FrontSide}}<hr id="answer">{{Singular}}<br>'
                '<span class="plural">{{Plural}}</span>'
            ),
        },
    ]
)


def colorize(word):
    colors = {
        ARTICLE_NEUTER: COLOR_NEUTER,
        ARTICLE_FEMININE: COLOR_FEMININE,
        ARTICLE_MASCULINE: COLOR_MASCULINE,
    }

    try:
        color = colors[word[:3]]
        result = '<span style="color: {color}">{word}</span>'.format(
            color=color,
            word=word
        )
    except KeyError:
        result = word

    return result


def make_non_noun_note(de, ru):
    return genanki.Note(
        model=non_noun_model,
        fields=(de, ru)
    )


def make_noun_note(de, ru):
    singular, *plurals = [s.strip() for s in de.split(',')]

    if not plurals:
        return genanki.Note(
            model=noun_without_plurals_model,
            fields=(
                colorize(singular),
                ru,
            )
        )

    singular_without_article = singular.split()[-1]
    processed_plurals = []

    for plural in plurals:
        if plural == '=':  # same except article
            processed_plurals.append(
                'die {}'.format(singular_without_article)
            )
        elif plural.startswith('-'):  # change article and append suffix
            processed_plurals.append(
                'die {}{}'.format(singular_without_article, plural[1:])
            )
        else:
            processed_plurals.append(plural)

    return genanki.Note(
        model=noun_with_plurals_model,
        fields=(
            colorize(singular),
            ', '.join(processed_plurals),
            ru
        )
    )


def generate_notes(data):
    bs = bs4.BeautifulSoup(data, 'html.parser')
    rows = bs.find('tbody').find_all('tr')

    for row in rows:
        de, ru = [td.text.strip() for td in row.find_all('td')]

        if any(de.startswith(article) for article in ARTICLES):
            make_note = make_noun_note
        else:
            make_note = make_non_noun_note

        yield make_note(de, ru)


with open('words.html') as f:
    raw_data = f.read()

deck = genanki.Deck(DECK_ID, 'German-Russian Deck')

for note in generate_notes(raw_data):
    deck.add_note(note)

genanki.Package(deck).write_to_file('de-ru.apkg')
