
<template>
  <div class="app-container">
    <el-row>
      <el-col :span="10">
        <el-button v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.authGame.auth_create" size="small" type="primary" @click="new_data">新增</el-button>
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
      <el-table-column prop="id" label="ID" width="70"/>
			<el-table-column prop="game_name_cn" label="游戏名称"/>
      <el-table-column prop="auth_type" label="权限"/>
				
      <el-table-column fixed="right" label="操作" align="center">
        <template slot-scope="scope" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.authGame.auth_update">
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
      width="30%"
      center>
      <div>
        <el-form ref="ruleForm" :model="ruleForm" :rules="rules" label-width="100px">
          <el-form-item label="权限名称" prop="auth">
            <el-select size="small" v-model="ruleForm.auth" placeholder="请选择权限名称" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in authData"
                :key="item.id"
                :label="item.auth_type"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="游戏名称" prop="game">
            <el-select size="small" v-model="ruleForm.game" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in gameData"
                :key="item.id"
                :label="item.game_name_cn"
                :value="item.id">
              </el-option>
            </el-select>
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
          <el-form-item label="权限名称" prop="auth">
            <el-select size="small" v-model="ruleForm_patch.auth" placeholder="请选择权限名称" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in authData"
                :key="item.id"
                :label="item.auth_type"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="游戏名称" prop="game">
            <el-select size="small" v-model="ruleForm_patch.game" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in gameData"
                :key="item.id"
                :label="item.game_name_cn"
                :value="item.id">
              </el-option>
            </el-select>
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
  name: 'authGame',
  components: { Mysearch, Pagination },
  filters: {
    typeFilter(type) {
      const typeMap = {
        0: '普通版',
        1: 'VIP版'
      }
      return typeMap[type]
    },
    decideTypeFilter(type) {
      const typeMap = {
        0: '系统设定',
        1: '自定义'
      }
      return typeMap[type]
    }
  },
  data() {
    return {
      centerDialog: false,
      centerDialog_delete: false,
      centerDialog_patch: false,
      page_datas: [],
      ruleForm: {
        game: '',
        auth: ''
      },
      rules: {
        game: [
          { required: true, message: '请选择辅助类型', trigger: 'change' }
        ],
        auth: [
          { required: true, message: '请选择充值类型', trigger: 'change' }
        ]
      },
      ruleForm_patch: {
        
      },
      rules_patch: {
        
      },
      authData: [],
      gameData: [],
      delete_data: {},
      my_pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        search: '',
        search_type: '',
      }
    }
  },

  created: function() {
    this.get_need_data(this.my_pagination)
    this.get_auth_data()
    this.get_game_data()
  },

  methods: {
    get_need_data(params) {
      GetAjax('/authGame/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },

    get_auth_data(params) {
      GetAjax('/auth/', params).then(response => {
        const data = response.data
        this.authData = data
      })
    },

    get_game_data(params) {
      GetAjax('/game/', params).then(response => {
        const data = response.data
        this.gameData = data
      })
    },


    post_need_data(data) {
      PostAjax('/authGame/', data).then(response => {
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
      PatchAjax('/authGame/' + data.id + '/', data).then(response => {
        const authGame = response.data
        this.centerDialog_patch = false
        this.$refs['ruleForm_patch'].resetFields()
        this.$message({
          showClose: true,
          message: '修改成功！',
          type: 'success'
        })
        for (let index = 0; index < this.page_datas.length; index++) {
          if (this.page_datas[index].id === data.id) {
            this.page_datas.splice(index, 1, Object.assign({}, authGame))
            break
          }
        }
        // this.get_need_data(this.my_pagination)
      })
    },

    delete_need_data(data) {
      DeleteAjax('/authGame/' + data.id + '/', data).then(response => {
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
