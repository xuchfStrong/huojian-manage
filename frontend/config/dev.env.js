'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  BASE_API: '"http://192.168.0.194:8000"',
  // BASE_API: '"http://120.48.7.121:18671/huojian/"',
})
