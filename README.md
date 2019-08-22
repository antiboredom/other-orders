# Other Orders

Experiments in sorting.

For more information, or to use as a Twitter client, visit: https://otherorders.net

To run locally on your own texts:

Install:

1) clone this repo
2) run `pip install -r requirements.txt`

Run:

```bash
python weirdsort.py FILENAME.txt --sort SORTTYPE [--reverse]
```

`SORTTYPE` can be one of:

**adjectives,  advertising,  alphabetical, antisemitism,  chronological, cop, drilism, emoji, eroticism, favorites, gendered, goth, hashtags, kafka, length, marx, named_entities, neoliberal, nouns, numbers, retweets, shame, stop_words, ted, username, userposts, verbs**

Please note that the first time you run weirdsort on a text it will create a json file called `FILENAME.txt.analys.txt` that contains tagged sentences. 

---

As an example, the following will sort sentences in Capital Volume 1 in order of eroticism, from most to least:

```bash
python weirdsort.py sorted_capitol.txt --sort eroticism --reverse
```

Yielding the following (first 20 lines):

------------

they licked it (the thing represented to them) twice to their tongues, after which they seemed to consider the bargain satisfactorily concluded.

Their brain ceased to think, their eyes to see.

They became amphibious and lived, as an English author says, half on land and half on water, and withal only half on both.

Adam bit the apple, and thereupon sin fell on the human race.

At night, they slept in pairs in one of the stifling holes into which the bedroom was divided by partitions of board.

The smell of their fish rose to the noses of the great men.

Deo has commanded the work of the girls to be done by the Nymphs, and now they skip lightly over the wheels, so that the shaken axles revolve with their spokes and pull round the load of the revolving stones.

They therefore acted and transacted before they thought.

All bounds of morals and nature, age and sex, day and night, were broken down.

The remnant of the aborigines flung on the sea-shore tried to live by catching fish.

The straw cuts their mouths, with which they constantly moisten it, and their fingers.

Clothed in a few dirty rags, the legs naked far above the knees, hair and face besmeared with dirt, they learn to treat all feelings of decency and of shame with contempt.

The muscles of animals, when they are deprived of a proper amount of light, become soft and inelastic, the nervous power loses its tone from defective stimulation, and the elaboration of all growth seems to be perverted....

Jerome had to wrestle hard, not only in his youth with the bodily flesh, as is shown by his fight in the desert with the handsome women of his imagination, but also in his old age with the spiritual flesh.

Such are fish which we catch and take from their element, water, timber which we fell in the virgin forest, and ores which we extract from their veins.

A characteristic feature is, that, even down into the eighteenth century, the different trades were called "mysteries" (mystères);  into their secrets none but those duly initiated could penetrate.

It was, therefore, quite in order that the virgins, who, at the feast of the Goddess of Love, gave themselves up to strangers, should offer to the goddess the piece of money they received.

Several did not contain an atom of morphia.

The young people stolen, were thrown into the secret dungeons of Celebes, until they were ready for sending to the slave-ships.

the low language, which they are accustomed to hear from their tenderest years, the filthy, indecent, and shameless habits, amidst which, unknowing, and half wild, they grow up, make them in after-life lawless, abandoned, dissolute....

----------

