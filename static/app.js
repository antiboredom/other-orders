const sorts = [
  {
    qs: 'chronological',
    key: 'created_at',
    display: 'Chronologically',
    description: 'Items are ordered by date created.',
    orders: ['Oldest', 'Newest']
  },
  {
    qs: 'alphabetical',
    key: 'lower_text',
    display: 'Alphabetical',
    orders: ['Lowest', 'Highest'],
    description: 'Items are put into lower case and then ordered alphabetically, from A to Z'
  },
  {
    qs: 'favorites',
    key: 'favorites',
    display: 'Total Favorites',
    orders: ['Lowest', 'Highest'],
    description: 'Items are ordered by total favorites received.'
  },
  {
    qs: 'retweets',
    key: 'retweets',
    display: 'Total Retweets',
    orders: ['Lowest', 'Highest'],
    description: 'Items are ordered by total retweets.'
  },
  {
    qs: 'length',
    key: 'length',
    display: 'Length of Tweet',
    orders: ['Shortest', 'Longest'],
    description: 'Items are ordered by total number of characters, including spaces.'
  },
  {
    qs: 'hashtags',
    key: 'total_hashtags',
    display: 'Total Hashtags',
    orders: ['Least', 'Most'],
    description: 'Items are ordered by total number of hashtags.'
  },
  {
    qs: 'username',
    key: 'username',
    display: 'Alphabetical by Username',
    orders: ['Lowest', 'Highest'],
    description: 'Items are ordered alphabetically, by the name of the their author.'
  },
  {
    qs: 'userposts',
    key: 'total_userposts',
    display: 'Total All-Time Posts from User',
    orders: ['Least', 'Most'],
    description: 'Items are ordered by how many posts their author has made over all time.'
  },
  {
    qs: 'marx',
    key: 'marx',
    display: 'Crudely Understood Marxism',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered relative to their semantic similarity to the phrase "workers must seize the means of production."'
  },
  {
    qs: 'kafka',
    key: 'kafka',
    display: 'Kafkaesque-ness',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered relative to their semantic similarity to the phrase "Hope exists, but not for us. My father judges me."'
  },
  {
    qs: 'shame',
    key: 'shame',
    display: 'Approximate Quantity of Shame Expressed',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered relative to their semantic similarity to the phrases that express remorse, regret, shame and embarrassment'
  },
  {
    qs: 'ted',
    key: 'ted',
    display: 'Similarity to Values Expressed in TED Talks',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered relative to their semantic similarity to a sentiment expressed regularly by Silicon Valley and its apologists'
  },
  {
    qs: 'emoji',
    key: 'total_emoji',
    display: 'Total Emoji',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered by how many emoji they contain, as determined by the regular expression [U00010000-U0010ffff]'
  },
  {
    qs: 'nouns',
    key: 'total_noun',
    display: 'Density of Nouns',
    orders: ['Lowest', 'Highest'],
    description:
      'Items are ordered by quantity of nouns, singular or plural, as a percentage of total words.'
  },
  {
    qs: 'verbs',
    key: 'total_verb',
    display: 'Density of Verbs',
    orders: ['Lowest', 'Highest'],
    description:
      'Items are ordered by quantity of verbs, of any conjugation, as a percentage of total words.'
  },
  {
    qs: 'adjectives',
    key: 'total_adj',
    display: 'Density of Adjectives',
    orders: ['Lowest', 'Highest'],
    description: 'Items are ordered by quantity of adjectives as a percentage of total words.'
  },
  {
    qs: 'numbers',
    key: 'total_num',
    display: 'Number of Numbers',
    orders: ['Least', 'Most'],
    description: 'Items are ordered by quantity of numbers as a percentage of total words.'
  },
  {
    qs: 'stop_words',
    key: 'total_stop',
    display: 'Percentage of Words Which Are Filler Words',
    orders: ['Lowest', 'Highest'],
    description:
      'Items are ordered by quantity of "stop" words, or words which are typically ignored by natural language processing systems.'
  },
  {
    qs: 'named_entities',
    key: 'total_entities',
    display: 'Density of People, Places, Brands, Monetary Values and Dates',
    orders: ['Lowest', 'Highest'],
    description:
      'Items are ordered by quantity of "named entities", words or phrases which may be proper nouns, monetary values or dates.'
  },
  {
    qs: 'antisemitism',
    key: 'antisemitism',
    display: 'Antisemitism as It Is Understood by the Right',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered by a particular definition of antisemitism, as determined by the item\'s "negativity" ranking from NLTK\'s sentiment analysis tool, coupled with occurrences of the word "Israel." That is, if the item has negative sentiment and also contains the word Israel, it is deemed antisemitic.'
  },
  {
    qs: 'eroticism',
    key: 'erotic',
    display: 'Eroticism as an Approximation of Similarity to a Sentence by Anaïs Nin',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered relative to their semantic similarity to the following passage by Anaïs Nin: "They ceased to be three bodies. They became all mouths and fingers and tongues and senses."'
  },
  {
    qs: 'drilism',
    key: '__label__dril',
    display: 'Similarity to @dril I.E. "drilism"',
    orders: ['Least', 'Most'],
    description: 'Items are ordered by "drilism", or by how closely they resemble tweets by @dril.'
  },
  {
    qs: 'cop',
    key: ['__label__CommissBratton'],
    display: 'Cop-Like',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered by how confidently they can be classified as phrases written by NYPD Commissioner Bratton.'
  },
  {
    qs: 'goth',
    key: '__label__sosadtoday',
    display: 'Gothness',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered by how confidently they can be classified as tweets posted by @sosadtoday.'
  },
  {
    qs: 'neoliberal',
    key: ['__label__ThirdWayTweet', '__label__ChelseaClinton'],
    display: 'Neoliberalism as Determined by Proximity to Famous Neoliberals',
    orders: ['Least', 'Most'],
    description: 'Items are ordered by their similarity to tweets by Chelsea Clinton'
  },
  {
    qs: 'advertising',
    key: ['__label__amazon'],
    display:
      'Use of Language Similar to Language Used by Corporate Social Media Accounts Such as Amazon',
    orders: ['Lowest', 'Highest'],
    description: 'Items are ordered by their similarity to tweets Amazon.'
  },
  {
    qs: 'gendered',
    key: 'total_gendered',
    display: 'Quantity of Gendered Words',
    orders: ['Least', 'Most'],
    description:
      'Items are ordered by total quantity of gendered words such as he, she, and actress.'
  }
].sort((a, b) => a.display.localeCompare(b.display));
// ].sort((a, b) => a.display.length - b.display.length);

let app = new Vue({
  el: '#app',
  delimiters: ['<%', '%>'],
  data: {
    message: 'Hello Vue!',
    tweets: [],
    sorter: sorts[0],
    sorts: sorts,
    reversed: false,
    loading: false
  },
  created() {
    let tweets = localStorage.getItem('tweets');
    if (tweets) {
      this.tweets = JSON.parse(tweets);
    } else {
      this.fetch();
    }
  },
  computed: {
    sortedTweets() {
      return this.tweets.sort((a, b) => {
        let val = 0;

        if (typeof a[this.sorter.key] === 'string') {
          val = a[this.sorter.key].localeCompare(b[this.sorter.key]);
        } else {
          if (Array.isArray(this.sorter.key)) {
            // let avals = this.sorter.key.reduce((j, k) => a[j]+a[k], 0);
            // let bvals = this.sorter.key.reduce((j, k) => b[j]+b[k], 0);
            // console.log(avals, bvals);
            // val = avals - bvals;
            val = a[this.sorter.key[0]] - b[this.sorter.key[0]];
          } else {
            val = a[this.sorter.key] - b[this.sorter.key];
          }
        }

        if (val == 0) val = a.tweet_id.localeCompare(b.tweet_id);

        if (this.reversed) val *= -1;

        return val;
      });
    }
  },

  methods: {
    onSort(sorter, event) {
      event.preventDefault();
      this.sorter = sorter;
    },

    fetch() {
      this.loading = true;

      let xhr = new XMLHttpRequest();
      // xhr.open('GET', '/tweets?testing=true');
      xhr.open('GET', '/tweets');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onload = () => {
        if (xhr.status === 200) {
          let response = JSON.parse(xhr.responseText);
          if (response.error) {
            console.log(response);
          } else {
            let tweets = JSON.parse(xhr.responseText);
            localStorage.setItem('tweets', xhr.responseText);
            this.tweets = tweets;
          }
        } else {
          console.log('error');
        }

        this.loading = false;
      };
      xhr.send();
    }
  }
});
