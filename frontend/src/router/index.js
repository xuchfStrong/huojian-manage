import Vue from 'vue'
import Router from 'vue-router'
Vue.use(Router)

/* Layout */
import Layout from '../views/layout/Layout'
export const constantRouterMap = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/404', component: () => import('@/views/404'), hidden: true },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/helper/chargeHelper'),
      meta: { title: '辅助充值', icon: 'dashboard', noCache: true }
    }]
  },
  {
    path: '/demoadmin',
    component: Layout,
    hidden: true,
    children: [
      {
        path: 'demo',
        name: 'demo',
        component: () => import('@/views/myviews/demoadmin01'),
        meta: { title: 'demo admin', icon: 'form' }
      }
    ]
  },
  {
    path: '/print',
    component: Layout,
    hidden: true,
    children: [
      {
        path: 'pdemo',
        name: 'pdemo',
        component: () => import('@/views/myviews/printdemo'),
        meta: { title: 'demo print', icon: 'form' }
      }
    ]
  },
  {
    path: '/tinymceDemo',
    component: Layout,
    hidden: true,
    children: [
      {
        path: 'tinymce',
        name: 'tinymce',
        component: () => import('@/views/myviews/tinymce_demo'),
        meta: { title: 'Tinymce Demo', icon: 'form' }
      }
    ]
  },
  {
    path: '/system',
    meta: { title: '系统管理', icon: 'form' },
    component: Layout,
    children: [
      
      {
        path: 'user',
        name: 'user',
        component: () => import('@/views/system/user'),
        meta: { title: '用户管理', icon: 'form' }
      },
      {
        path: 'auth',
        name: 'auth',
        component: () => import('@/views/system/auth'),
        meta: { title: '权限管理', icon: 'form' }
      },
    ]
  },
  {
    path: '/helper',
    meta: { title: '辅助管理', icon: 'form' },
    component: Layout,
    children: [
      {
        path: 'charge',
        name: 'charge',
        component: () => import('@/views/helper/charge'),
        meta: { title: '充值记录', icon: 'form' }
      },
      {
        path: 'chargeSum',
        name: 'chargeSum',
        component: () => import('@/views/helper/chargeSum'),
        meta: { title: '金额统计', icon: 'form' }
      },
      {
        path: 'game',
        name: 'game',
        component: () => import('@/views/helper/game'),
        meta: { title: '游戏管理', icon: 'form' }
      },
      {
        path: 'chargetype',
        name: 'chargetype',
        component: () => import('@/views/helper/chargetype'),
        meta: { title: '充值类型', icon: 'form' }
      },
      {
        path: 'price',
        name: 'price',
        component: () => import('@/views/helper/price'),
        meta: { title: '游戏价格', icon: 'form' }
      }
    ]
  },
  {
    path: '/userinfo',
    component: Layout,
    children: [{
      path: 'userinfo',
      name: 'Userinfo',
      component: () => import('@/views/userinfo/index'),
      meta: { title: '个人信息', icon: 'dashboard', noCache: true }
    }]
  },
  // {
  //   path: '/flow',
  //   meta: { title: '审批流', icon: 'form' },
  //   component: Layout,
  //   children: [
      
  //     {
  //       path: 'flowgroup',
  //       name: 'flowgroup',
  //       component: () => import('@/views/flow/flowgroup'),
  //       meta: { title: '审批组管理', icon: 'form' }
  //     },
  //     {
  //       path: 'approvalflow',
  //       name: 'approvalflow',
  //       component: () => import('@/views/flow/approvalflow'),
  //       meta: { title: '审批流设置', icon: 'form' }
  //     },
  //     {
  //       path: 'flowbody',
  //       name: 'flowbody',
  //       component: () => import('@/views/flow/flowbody'),
  //       meta: { title: '审批主体', icon: 'form' }
  //     },
  //   ]
  // },
  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({
  // mode: 'history', //后端支持可开
  // base: '/abc/',
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})
