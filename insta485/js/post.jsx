import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

class Post extends React.Component {
  /* Display number of image and post owner of a single post */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      timeStamp: '',
      ownerUrl: '',
      ownerImgUrl: '',
      postShowUrl: '',
      likes: '',
      lognameLikesThis: true,
      postid: '',
      comments: [],
      likeid: '',
      text: '',
    };

    this.changeCommentText = this.changeCommentText.bind(this);
    this.createComment = this.createComment.bind(this);
    this.likeUnlike = this.likeUnlike.bind(this);
    this.likeDoubleClick = this.likeDoubleClick.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
    this.DeleteButton = this.DeleteButton.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { data } = this.props;
    // Assign props into Post object
    const { url } = JSON.parse(data);
    console.log(url);
    fetch(url, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((info) => {
        // Fetch data for all posts
        this.setState({
          imgUrl: info.imgUrl,
          owner: info.owner,
          timeStamp: moment.utc(info.created).fromNow(),
          ownerUrl: info.ownerShowUrl,
          ownerImgUrl: info.ownerImgUrl,
          postShowUrl: info.postShowUrl,
          likes: info.likes.numLikes,
          lognameLikesThis: info.likes.lognameLikesThis,
          postid: info.postid,
          comments: [...info.comments],
          likeid: info.likes.url,
        });
        // console.log(info);
      })
      .catch((error) => console.log(error));
  }

  RenderComments(commentsList) {
    const taskList = commentsList.map((c) => (
      <div key={c.commentid} className="single_comment">
        <p>
          <a href={c.ownerShowUrl} key={c.commentid}>{c.owner}</a>
          <span> </span>
          {c.text}
        </p>
        {this.DeleteButton(c.commentid, c.lognameOwnsThis)}
      </div>
    ));
    return (taskList);
  }

  likeUnlike(event) {
    event.preventDefault();
    const { lognameLikesThis } = this.state;
    if (lognameLikesThis) {
      console.log('User unliked this post');
      const { likeid } = this.state;
      fetch(likeid, { method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response;
        })
        .then((info) => {
          console.log(info);
          this.setState((prevState) => ({
            likes: prevState.likes - 1,
          }));
          this.setState({ lognameLikesThis: false });
        })
        .catch((error) => console.log(error));
    } else {
      const str1 = '/api/v1/likes/?postid=';
      const { postid } = this.state;
      const url = str1.concat('', postid);
      fetch(url, { method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((info) => {
          console.log(info);
          this.setState((prevState) => ({
            likes: prevState.likes + 1,
          }));
          this.setState({ lognameLikesThis: true, likeid: info.url });
        })
        .catch((error) => console.log(error));
    }
  }

  likeDoubleClick(event) {
    event.preventDefault();
    const { lognameLikesThis } = this.state;
    if (!lognameLikesThis) {
      const str1 = '/api/v1/likes/?postid=';
      const { postid } = this.state;
      const url = str1.concat('', postid);
      fetch(url, { method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((info) => {
          console.log(info);
          this.setState((prevState) => ({
            likes: prevState.likes + 1,
          }));
          this.setState({ lognameLikesThis: true, likeid: info.url });
        })
        .catch((error) => console.log(error));
    }
  }

  createComment(event) {
    event.preventDefault();
    const { text } = this.state;
    const data = { text };
    const { postid } = this.state;
    const str1 = '/api/v1/comments/?postid=';
    const url = str1.concat('', postid);
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((info) => {
        this.setState((prevState) => ({
          comments: prevState.comments.concat(info),
        }));
        this.setState({ text: '' });
      })
      .catch((error) => console.log(error));
  }

  changeCommentText(event) {
    this.setState({ text: event.target.value });
  }

  DeleteButton(commentid, lognameOwnsThis) {
    if (lognameOwnsThis) {
      return (
        <button
          className="delete-comment-button"
          type="submit"
          onClick={this.deleteComment}
          commentid={commentid}
        >
          delete
        </button>
      );
    }
    return (null);
  }

  deleteComment(event) {
    // event.preventDefault();
    const commentidIn = event.currentTarget.getAttribute('commentid');
    const str1 = '/api/v1/comments/';
    const str2 = str1.concat('', commentidIn);
    const url = str2.concat('', '/');
    fetch(url, { method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response;
      })
      .then(() => {
        this.setState((prevState) => ({
          comments: prevState.comments.filter(
            (comment) => comment.commentid.toString() !== commentidIn.toString(),
          ),
        }));
      })
      .catch((error) => console.log(error));
  }

  render() {
    // Returns HTML representing this component
    // Use JSX template-like syntax here
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl,
      owner,
      timeStamp,
      ownerUrl,
      ownerImgUrl,
      postShowUrl,
      likes,
      lognameLikesThis,
      comments,
      postid,
      text,
    } = this.state;

    // Render number of post image and post owner
    return (
      <div key={postid} className="post">
        <div className="post-div">
          <a href={ownerUrl}>
            <img
              src={ownerImgUrl}
              alt="text"
              height="80"
              className="owner_img"
            />
          </a>
          <a className="profile" href={ownerUrl}>{owner}</a>
          <span> </span>
          <a href={postShowUrl}>
            <span className="time">
              {timeStamp}
            </span>
          </a>
          <p>
            <img src={imgUrl} onDoubleClick={this.likeDoubleClick} className="post-img" alt="text" />
          </p>
          <p className="likes">
            {likes}
            <span> </span>
            {likes === 1 ? 'like' : 'likes'}
          </p>
          <div>
            <button className="like-unlike-button" type="submit" onClick={this.likeUnlike}>
              {lognameLikesThis ? 'unlike' : 'like'}
            </button>
          </div>
          <div className="commentsList">
            {this.RenderComments(comments)}
          </div>
          <div className="create_comment">
            <form className="comment-form" onSubmit={this.createComment}>
              <input
                type="text"
                value={text}
                placeholder="Make Your Comment Here."
                onChange={this.changeCommentText}
              />
            </form>
          </div>
        </div>
      </div>
    );
  }
}

Post.propTypes = {
  data: PropTypes.string.isRequired,
};

export default Post;
