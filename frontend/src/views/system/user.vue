
<template>
  <div class="app-container">
    <el-row>
      <el-col :span="10">
        <el-button v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.user.auth_create" size="small" type="primary" @click="new_data">新增</el-button>
        <p></p>
      </el-col>
      <el-col :span="8"><p/></el-col>
      <!-- <el-col :span="4">
        <el-select size="small" v-model="my_pagination.search_type" placeholder="请选择" style="width: 100%" @change="my_change">
          <el-option label="全部分类" value=""/>
          <el-option label="测试分类" value="0"/>
          <el-option label="测试分类" value="1"/>
        </el-select>
      </el-col> -->
      <el-col :span="6">
        <mysearch v-model="my_pagination.search" @searchData="to_search"/>
      </el-col>
    </el-row>
    <br>
    <el-table
      :data="page_datas"
      border
      stripe
      size="mini"
      style="width: 100%">
      <el-table-column prop="id" label="ID"/>
			<el-table-column prop="username" label="用户名"/>
			<el-table-column prop="phone" label="手机号"/>
			<el-table-column prop="email" label="邮箱"/>
			<el-table-column prop="real_name" label="姓名"/>
			<el-table-column prop="group.group_type_cn" label="角色"/>
      <el-table-column prop="auth.auth_type" label="权限"/>
			<el-table-column prop="bf_logo_time" label="上次登录时间"/>
      <el-table-column label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button size="small" v-if="canEditUser" @click="edit_data(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.user.auth_destroy"  @click="delete_data_fuc(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <br>
    <pagination :total="my_pagination.count" :page.sync="my_pagination.page" :page_size.sync="my_pagination.page_size" @pagination="pag_change"/>

    <el-dialog
      :visible.sync="centerDialog"
      v-dialogDrag
      title="新增"
      width="50%"
      center>
      <div>
        <el-form ref="ruleForm" :model="ruleForm" :rules="rules" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input size="small" v-model="ruleForm.username"/>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input size="small" type="password" v-model="ruleForm.password"/>
          </el-form-item>
          <el-form-item label="角色" prop="group">
            <el-select size="small" v-model="ruleForm.group" placeholder="请选择角色" filterable clearable style="width: 100%;">
              <el-option v-for="item in groupTypeList" :key="item.id" :label="item.label" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="上级" v-if="ruleForm.group == 4" prop="parent_id">
            <el-select size="small" v-model="ruleForm.parent_id" placeholder="请选择上级" filterable clearable style="width: 100%;">
              <el-option v-for="item in userList" :key="item.id" :label="item.username" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="权限" prop="auth">
            <el-select size="small" v-model="ruleForm.auth" placeholder="请选择权限" filterable clearable style="width: 100%;">
              <el-option v-for="item in auth_datas" :key="item.id" :label="item.auth_type" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input size="small" v-model="ruleForm.phone"/>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input size="small" v-model="ruleForm.email"/>
          </el-form-item>
          <el-form-item label="姓名" prop="real_name">
            <el-input size="small" v-model="ruleForm.real_name"/>
          </el-form-item>
          <el-form-item label="状态" required>
            <el-switch size="small"
              v-model="ruleForm.status"
              :active-value="1"
              :inactive-value="0"
              active-color="#13ce66"
              inactive-color="#ff4949" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input size="small" v-model="ruleForm.content" type="textarea"/>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button size="small" @click="resetForm('ruleForm')">取 消</el-button>
        <el-button size="small" type="primary" @click="submitForm('ruleForm')">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog
      :visible.sync="centerDialog_delete"
      v-dialogDrag
      title="确认删除"
      width="30%"
      center>
      <span>是否确认删除，删除后不可恢复？</span>
      <span slot="footer" class="dialog-footer">
        <el-button size="small" @click="centerDialog_delete = false">取 消</el-button>
        <el-button size="small" type="primary" @click="true_delete">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog
      :visible.sync="centerDialog_patch"
      title="编辑"
      width="50%"
      center>
      <div>
        <el-form ref="ruleForm_patch" :model="ruleForm_patch" :rules="rules" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input size="small" v-model="ruleForm_patch.username"/>
          </el-form-item>
          <el-form-item label="密码">
            <el-input size="small" type="password" v-model="ruleForm_patch.password"/>
          </el-form-item>
          <el-form-item label="角色" prop="group">
            <el-select size="small" v-model="ruleForm_patch.group" placeholder="请选择角色" filterable clearable style="width: 100%;">
              <el-option v-for="item in groupTypeList" :key="item.id" :label="item.label" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="上级" v-if="ruleForm_patch.group == 4" prop="parent_id">
            <el-select size="small" v-model="ruleForm_patch.parent_id" placeholder="请选择上级" filterable clearable style="width: 100%;">
              <el-option v-for="item in userList" :key="item.id" :label="item.username" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="权限" prop="auth">
            <el-select size="small" v-model="ruleForm_patch.auth" placeholder="请选择权限" filterable clearable style="width: 100%;">
              <el-option v-for="item in auth_datas" :key="item.id" :label="item.auth_type" :value="item.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input size="small" v-model="ruleForm_patch.phone"/>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input size="small" v-model="ruleForm_patch.email"/>
          </el-form-item>
          <el-form-item label="姓名" prop="real_name">
            <el-input size="small" v-model="ruleForm_patch.real_name"/>
          </el-form-item>
          <el-form-item label="状态" required>
            <el-switch size="small"
              v-model="ruleForm_patch.status"
              :active-value="1"
              :inactive-value="0"
              active-color="#13ce66"
              inactive-color="#ff4949" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input size="small" v-model="ruleForm_patch.content" type="textarea"/>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button size="small" @click="resetForm('ruleForm_patch')">取 消</el-button>
        <el-button size="small" type="primary" @click="submitForm('ruleForm_patch')">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>
<style>
.el-table .cell .el-tooltip {
  white-space: pre-line;
}
</style>
<script>
import store from '@/store'
import Vue from 'vue'
import { GetAjax, PostAjax, PatchAjax, DeleteAjax } from '@/api/myapi'
import datetime from 'date-and-time'
import Mysearch from '@/components/SearchField/index2.vue'
import Pagination from '@/components/Pagination'
import UploadImage from '@/components/Upload/singleImage.vue'
import UploadFile from '@/components/Upload/singleFile.vue'
// import Tinymce from '@/components/Tinymce/index.vue'

export default {
  name: 'userManage',
  components: { Mysearch, Pagination, UploadImage, UploadFile },
  data() {
    return {
      centerDialog: false,
      centerDialog_delete: false,
      centerDialog_patch: false,
      page_datas: [],
      userList: [],
      groupTypeList: [
        {label: '管理员', id: 2},
        {label: '一级代理', id: 3},
        {label: '二级代理', id: 4}
      ],
      ruleForm: {
        username: '',
        password: '',
        phone: '',
        email: '',
        content: '',
        auth: '',
        status: false,
        group: '',
        parent_id: null,
        real_name: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        real_name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' }
        ],
        group: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ],
        auth: [
          { required: true, message: '请选择权限', trigger: 'change' }
        ],
        parent_id: [
          { required: true, message: '请选择上级', trigger: 'change' }
        ],
      },
      ruleForm_patch: {
        
      },
      rules_patch: {
        
      },
      delete_data: {},
      my_pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        search: '',
        search_type: '',
      },
      auth_datas: []
    }
  },
  computed: {
    canEditUser() {
      return this.$store.getters.user_obj.group.group_type === 'SuperAdmin' || 
      (this.$store.getters.auth_json.user.auth_update && this.$store.getters.auth_json.auth.auth_list)
    }
  },
  created: function() {
    this.get_need_data(this.my_pagination)
    this.get_auth_data()
    this.getUserList()
  },
  methods: {
    get_need_data(params) {
      GetAjax('/user/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },
    get_auth_data(params) {
      if (!this.canEditUser) return
      GetAjax('/auth/', params).then(response => {
        const data = response.data
        this.auth_datas = data
      })
    },
    getUserList() {
      GetAjax('/user/').then(response => {
        const data = response.data
        const GroupType = ['NormalUser']
        this.userList = data.filter(item => {
          return GroupType.includes(item.group.group_type)
        })
      })
    },
    post_need_data(data) {
      if (!data.parent_id) data.parent_id = null
      PostAjax('/user/', data).then(response => {
        const data = response.data
        this.centerDialog = false
        this.$refs['ruleForm'].resetFields()
        this.$message({
          showClose: true,
          message: '新增成功！',
          type: 'success'
        })
        this.get_need_data(this.my_pagination)
      })
    },
    patch_need_data(data) {
      if (!data.parent_id) data.parent_id = null
      PatchAjax('/user/' + data.id + '/', data).then(response => {
        const data = response.data
        this.centerDialog_patch = false
        this.$refs['ruleForm_patch'].resetFields()
        this.$message({
          showClose: true,
          message: '修改成功！',
          type: 'success'
        })
        this.get_need_data(this.my_pagination)
      })
    },
    delete_need_data(data) {
      DeleteAjax('/user/' + data.id + '/', data).then(response => {
        const data = response.data
        this.centerDialog_delete = false
        this.$message({
          showClose: true,
          message: '删除成功！',
          type: 'success'
        })
        this.get_need_data(this.my_pagination)
      })
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (formName == 'ruleForm') {
            // datetime.format(this.ruleForm.date, 'YYYY-MM-DD')
            // console.log(datetime.format(this.ruleForm.time, 'hh:mm:ss'))
            this.post_need_data(this.ruleForm)
          } else {
            this.patch_need_data(this.ruleForm_patch)
          }
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    // form数据验证
    resetForm(formName) {
      this.centerDialog = false
      this.centerDialog_patch = false
      this.$refs[formName].resetFields()
    },
    // 删除按钮
    delete_data_fuc(row) {
      this.delete_data = row
      this.centerDialog_delete = true
    },
    // 新增按钮
    new_data() {
      this.centerDialog = true
    },
    // 确定删除按钮
    true_delete() {
      this.delete_need_data(this.delete_data)
    },
    // 编辑按钮
    edit_data(row) {
      this.ruleForm_patch = JSON.parse(JSON.stringify(row))
      this.ruleForm_patch.group = row.group.id
      if (row.auth) {
        this.ruleForm_patch.auth = row.auth.id
      }
      this.centerDialog_patch = true
    },
    // 搜索层相关
    to_search() {
      this.my_pagination.page = 1
      this.get_need_data(this.my_pagination)
    },
    pag_change() {
      this.get_need_data(this.my_pagination)
    },
    search_change() {
      this.get_need_data(this.my_pagination)
    },
    my_change(val) {
      this.my_pagination.page = 1
      this.my_pagination.search_type = val
      this.get_need_data(this.my_pagination)
    }
  }
}
</script>

<style scoped>
</style>  
