import React from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import PropTypes from 'prop-types';
import Post from './post';

class MultiPosts extends React.Component {
  constructor(props) {
    super(props);
    this.state = { links: [], next: '' };
    this.fetchNext = this.fetchNext.bind(this);
  }

  componentDidMount() {
    // check if the user goes back
    const perfEntries = performance.getEntriesByType('navigation')[0];
    const IF_BACKFORWARD = perfEntries === 'back_forward';
    if (IF_BACKFORWARD) {
      this.setState({
        links: window.history.state.links,
        next: window.history.state.next,
      });
    } else {
      const { url } = this.props;
      fetch(url, { credentials: 'same-origin', method: 'GET' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // Fetch data for all posts
          this.setState({
            links: data.results, // list of all posts
            next: data.next,
          });
          // console.log(data);
        })
        .catch((error) => console.log(error));
    }
  }

  fetchNext() {
    const { next } = this.state;
    fetch(next, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      }).then((data) => {
        this.setState((prevState) => ({
          links: prevState.links.concat(data.results),
          next: data.next,
        }));
      }).catch((error) => console.log(error));
    window.history.replaceState(this.state, 'title');
  }

  render() {
    const { links, next } = this.state;
    return (
      <InfiniteScroll
        onunload={() => {
          window.history.replaceState(this.state, 'title');
        }}
        endMessage={(
          <p style={{ textAlign: 'center' }}>
            You reach the bottom of the page
          </p>
        )}
        loader={<h4 style={{ textAlign: 'center' }}>Loading...</h4>}
        hasMore={next !== ''}
        next={this.fetchNext}
        dataLength={links.length}
      >
        <div className="PostArea">
          {links.map((post) => (
            <div key={post.postid}>
              <Post data={JSON.stringify(post)} />
            </div>
          ))}
        </div>
      </InfiniteScroll>
    );
  }
}
MultiPosts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default MultiPosts;
