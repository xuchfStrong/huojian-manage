
<template>
  <div class="app-container">
    <el-row>
      <el-col :span="10">
        <el-button v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.game.auth_create" size="small" type="primary" @click="new_data">新增</el-button>
        <p></p>
      </el-col>
      <el-col :span="8"><p/></el-col>
      <el-col :span="6">
        <mysearch v-model="my_pagination.search" @searchData="to_search"/>
      </el-col>
    </el-row>
    <br>
    <el-table
      :data="page_datas"
      border
      stripe
      style="width: 100%">
			<el-table-column prop="game_name_cn" label="游戏名"/>
      <el-table-column prop="game_name" label="游戏代码"/>
			<el-table-column prop="charge_url" label="充值接口"/>
			<el-table-column prop="query_url" label="查询接口"/>
			<el-table-column prop="reset_url" label="撤销接口"/>
			<el-table-column prop="content" label="备注"/>
				
      <el-table-column label="操作" align="center">
        <template slot-scope="scope" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.game.auth_update">
          <el-button size="mini" @click="edit_data(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="delete_data_fuc(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <br>
    <pagination 
      :total="my_pagination.count" 
      :page.sync="my_pagination.page" 
      :page_size.sync="my_pagination.page_size" 
      @pagination="pag_change"/>

    <el-dialog
      :visible.sync="centerDialog"
      :close-on-press-escape="false"
      :close-on-click-modal="false"
      v-dialogDrag
      title="新增"
      width="50%"
      center>
      <div>
        <el-form ref="ruleForm" :model="ruleForm" :rules="rules" label-width="100px">
          <el-form-item label="游戏名称" prop="game_name_cn">
            <el-input size="small" v-model="ruleForm.game_name_cn"/>
          </el-form-item>
          <el-form-item label="游戏代码" prop="game_name">
            <el-input size="small" v-model="ruleForm.game_name"/>
          </el-form-item>
          <el-form-item label="充值接口" prop="charge_url">
            <el-input size="small" v-model="ruleForm.charge_url"/>
          </el-form-item>
          <el-form-item label="查询接口" prop="query_url">
            <el-input size="small" v-model="ruleForm.query_url"/>
          </el-form-item>
          <el-form-item label="撤销接口" prop="reset_url">
            <el-input size="small" v-model="ruleForm.reset_url"/>
          </el-form-item>
          <el-form-item label="游戏备注" prop="content">
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
      :close-on-press-escape="false"
      :close-on-click-modal="false"
      title="编辑"
      width="50%"
      center>
      <div>
        <el-form ref="ruleForm_patch" :model="ruleForm_patch" :rules="rules" label-width="100px">
          <el-form-item label="游戏名称" prop="game_name_cn">
            <el-input size="small" v-model="ruleForm_patch.game_name_cn"/>
          </el-form-item>
          <el-form-item label="游戏代码" prop="game_name">
            <el-input size="small" v-model="ruleForm_patch.game_name"/>
          </el-form-item>
          <el-form-item label="充值接口" prop="charge_url">
            <el-input size="small" v-model="ruleForm_patch.charge_url"/>
          </el-form-item>
          <el-form-item label="查询接口" prop="query_url">
            <el-input size="small" v-model="ruleForm_patch.query_url"/>
          </el-form-item>
          <el-form-item label="撤销接口" prop="reset_url">
            <el-input size="small" v-model="ruleForm_patch.reset_url"/>
          </el-form-item>
          <el-form-item label="游戏备注" prop="content">
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

<script>
import store from '@/store'
import { GetAjax, PostAjax, PatchAjax, DeleteAjax } from '@/api/myapi'
import Mysearch from '@/components/SearchField/index2.vue'
import Pagination from '@/components/Pagination'

export default {
  name: 'gameManage',
  components: { Mysearch, Pagination },
  data() {
    return {
      centerDialog: false,
      centerDialog_delete: false,
      centerDialog_patch: false,
      page_datas: [],
      ruleForm: {
        game_name_cn: '',
        game_name: '',
        charge_url: '',
        query_url: '',
        reset_url: '',
        content: ''
      },
      rules: {
        game_name_cn: [
          { required: true, message: '请输入游戏名称', trigger: 'blur' }
        ],
        game_name: [
          { required: true, message: '请输入游戏代码', trigger: 'blur' }
        ],
        charge_url: [
          { required: true, message: '请输入充值接口', trigger: 'blur' }
        ],
        query_url: [
          { required: true, message: '请输入查询接口', trigger: 'blur' }
        ],
        reset_url: [
          { required: true, message: '请输入撤销接口', trigger: 'blur' }
        ]
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

  created: function() {
    this.get_need_data(this.my_pagination)
  },

  methods: {
    get_need_data(params) {
      GetAjax('/game/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },

    post_need_data(data) {
      PostAjax('/game/', data).then(response => {
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
      PatchAjax('/game/' + data.id + '/', data).then(response => {
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
      DeleteAjax('/game/' + data.id + '/', data).then(response => {
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


<style>
.el-table .cell .el-tooltip {
  white-space: pre-line;
}
</style>
<style scoped>
</style>  
