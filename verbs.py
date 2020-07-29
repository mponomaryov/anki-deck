import genanki


DECK_ID = 7469112283
MODULE_ID = 2417888824

CSS = '''
.card {
    font-family: arial;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    color: black;
    background-color: white;
}

.preterite::before,
.partizip2::before {
    color: gray;
    font-size: 70%;
    font-weight: normal;
    font-style: italic;
}

.preterite::before {
    content: "Preterite: ";
}

.partizip2::before {
    content: "Partizip 2: ";
}
'''

Model = genanki.Model(
    MODULE_ID,
    fields = [
        {'name': 'Infinitive'},
        {'name': 'Preterite'},
        {'name': 'Partizip2'},
        {'name': 'Translation'},
    ],
    css=CSS,
    templates=[
        {
            'name': 'Card 1',
            'qfmt': (
                '{{Infinitive}}<br>'
                '<span class="preterite">{{Preterite}}</span><br>'
                '<span class="partizip2">{{Partizip2}}</span>'
            ),
            'afmt': '{{FrontSide}}<hr id="answer">{{Translation}}'
        },
        {
            'name': 'Card 2',
            'qfmt': '{{Translation}}',
            'afmt': (
                '{{FrontSide}}<hr id="answer">'
                '{{Infinitive}}<br>'
                '<span class="preterite">{{Preterite}}</span><br>'
                '<span class="partizip2">{{Partizip2}}</span>'
            ),
        },
    ]
)

deck = genanki.Deck(DECK_ID, 'German Verbs')

with open('german_verbs.txt') as file:
    for line in file:
        infinitive, translation, preterite, partizip2 = line.strip().split('|')

        if infinitive.endswith('*'):
            infinitive = f'<span style="color: red">{infinitive[:-1]}</span>'

        deck.add_note(
            genanki.Note(
                model=Model,
                fields=(infinitive, preterite, partizip2, translation)
            )
        )

genanki.Package(deck).write_to_file('GermanVerbs.apkg')
