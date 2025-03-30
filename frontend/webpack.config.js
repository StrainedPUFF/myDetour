const path = require('path');
const WebpackBundleTracker = require('webpack-bundle-tracker');

module.exports = {
  mode: 'development', // Use 'production' for production builds
  entry: './src/index.js', // Entry point for your application
  output: {
    path: path.resolve(__dirname, 'staticfiles/'), // Output directory
    filename: 'main.js', // Name of the bundled file
  },
  plugins: [
    new WebpackBundleTracker({
      path: __dirname,
      filename: 'webpack-stats.json', // Tracks Webpack assets for Django
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/, // Transpile JavaScript files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'], // Ensure React and modern JavaScript support
            plugins: ['@babel/plugin-syntax-jsx'],
          },
        },
      },
      {
        test: /\.css$/, // Process CSS files
        use: ['style-loader', 'css-loader'], // Ensure styles are handled
      },
      {
        test: /\.(png|jpg|gif|svg)$/, // Handle image assets
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]', // Preserve the file name
              outputPath: 'images/', // Save images in an 'images' folder within 'staticfiles'
            },
          },
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'], // Resolve JavaScript and React files
  },
  devtool: 'source-map', // Enable source maps for easier debugging
  externals: {
    react: 'React',
    'react-dom': 'ReactDOM',
  }  
};
