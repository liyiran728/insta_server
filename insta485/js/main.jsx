import React from 'react';
import ReactDOM from 'react-dom';
import MultiPosts from './MultiPosts';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <MultiPosts url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
