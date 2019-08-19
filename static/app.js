const sorts = [
  {
    qs: 'chronological',
    key: 'created_at',
    display: 'Chronologically',
    description: 'Items are ordered by date created',
    orders: ['Oldest', 'Newest']
  },
  {qs: 'alphabetical', key: 'lower_text', display: 'Alphabetically', orders: ['Lowest', 'Highest']},
  {qs: 'favorites', key: 'favorites', display: 'Total Favorites', orders: ['Lowest', 'Highest']},
  {qs: 'retweets', key: 'retweets', display: 'Total Retweets', orders: ['Lowest', 'Highest']},
  {qs: 'length', key: 'length', display: 'Length of Tweet', orders: ['Shortest', 'Longest']},
  {qs: 'hashtags', key: 'total_hashtags', display: 'Total Hashtags', orders: ['Least', 'Most']},
  {
    qs: 'username',
    key: 'username',
    display: 'Alphabetically by Username',
    orders: ['Lowest', 'Highest']
  },
  {
    qs: 'userposts',
    key: 'total_userposts',
    display: 'Total All-Time Posts From User',
    orders: ['Least', 'Most']
  },
  {qs: 'marx', key: 'marx', display: 'Marxism', orders: ['Least', 'Most']},
  {qs: 'kafka', key: 'kafka', display: 'Kafkaesque-ness', orders: ['Least', 'Most']},
  {
    qs: 'shame',
    key: 'shame',
    display: 'Approximate Quantity of Shame Expressed',
    orders: ['Least', 'Most']
  },
  {
    qs: 'ted',
    key: 'ted',
    display: 'Similarity To Values Expressed In TED Talks',
    orders: ['Least', 'Most']
  },
  {qs: 'emoji', key: 'total_emoji', display: 'Total Emoji', orders: ['Least', 'Most']},
  {qs: 'nouns', key: 'total_noun', display: 'Density of Nouns', orders: ['Lowest', 'Highest']},
  {qs: 'verbs', key: 'total_verb', display: 'Density of Verbs', orders: ['Lowest', 'Highest']},
  {
    qs: 'adjectives',
    key: 'total_adj',
    display: 'Density of Adjectives',
    orders: ['Lowest', 'Highest']
  },
  {qs: 'numbers', key: 'total_num', display: 'Number of Numbers', orders: ['Least', 'Most']},
  {
    qs: 'stop_words',
    key: 'total_stop',
    display: 'Percentage of Words which are Filler Words',
    orders: ['Lowest', 'Highest']
  },
  {
    qs: 'named_entities',
    key: 'total_entities',
    display: 'Density of People, Places, Brands, Monetary Values and Dates',
    orders: ['Lowest', 'Highest']
  },
  {
    qs: 'antisemitism',
    key: 'antisemitism',
    display: 'Antisemitism as it is Understood by the Right',
    orders: ['Least', 'Most']
  },
  {
    qs: 'eroticism',
    key: 'erotic',
    display: 'Eroticism as an approximation of Similarity to a Sentence by Anais Nin',
    orders: ['Least', 'Most']
  },
  {
    qs: 'drilism',
    key: '__label__dril',
    display: 'Similarity to @dril IE "drilism"',
    orders: ['Least', 'Most']
  },
  {qs: 'cop', key: ['__label__CommissBratton'], display: 'Cop-Like', orders: ['Least', 'Most']},
  {qs: 'goth', key: '__label__sosadtoday', display: 'Gothness', orders: ['Least', 'Most']},
  {
    qs: 'neoliberal',
    key: ['__label__ThirdWayTweet', '__label__ChelseaClinton'],
    display: 'Neoliberalism as determined by proximity to Famous Neoliberals',
    orders: ['Least', 'Most']
  },
  {
    qs: 'advertising',
    key: ['__label__amazon'],
    display:
      'Use of Language Similar To Language used by Corporate Social Media Accounts Such as Amazon',
    orders: ['Lowest', 'Highest']
  },
  {
    qs: 'gendered',
    key: 'total_gendered',
    display: 'Total Number of Gendered Words',
    orders: ['Least', 'Most']
  }
];

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
    this.fetch();
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
            val = a[this.sorter.key[0]] - b[this.sorter.key[0]]
          } else {
            val = a[this.sorter.key] - b[this.sorter.key];
          }
        }

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
      xhr.open('GET', '/tweets?testing=true');
      // xhr.open('GET', '/tweets');
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onload = () => {
        if (xhr.status === 200) {
          let response = JSON.parse(xhr.responseText);
          if (response.error) {
            console.log(response);
          } else {
            let tweets = JSON.parse(xhr.responseText);
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
