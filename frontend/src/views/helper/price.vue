
<template>
  <div class="app-container">
    <el-form :inline="true" size="mini" class="search_form_wrapper_small" label-width="90px"  label-position="right">
      <div class="btn-form-item">
        <el-button type="primary" size="mini" @click="to_search"> 搜索</el-button>
        <el-button v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.price.auth_create" type="primary" size="mini" @click="new_data">新增</el-button>
      </div>

      <el-form-item label="充值类型:">
        <el-select size="mini" v-model="my_pagination.charge_type_id" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in chargetypeList"
            :key="item.id"
            :label="item.type_name_cn"
            :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="游戏:" >
        <el-select size="mini" v-model="my_pagination.game_id" placeholder="请选择游戏" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in gameList"
            :key="item.game"
            :label="item.game_name_cn"
            :value="item.game">
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <div class="tips">提示：这里没有配置的游戏就采用充值类型中默认的值。</div>
    <el-table
      :data="page_datas"
      size="mini"
      border
      stripe
      style="width: 100%">
			<el-table-column prop="game_name_cn" label="游戏名"/>
      <el-table-column prop="charge_type_name_cn" label="充值类型"/>
      <el-table-column prop="status" label="状态"/>
			<el-table-column prop="charge_value" label="金额"/>
      <el-table-column label="操作" align="center" width="150">
        <template slot-scope="scope" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.price.auth_update">
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
          <el-form-item label="游戏名称" prop="game">
            <el-select size="mini" v-model="ruleForm.game" placeholder="请选择游戏" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in gameList"
                :key="item.game"
                :label="item.game_name_cn"
                :value="item.game">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="充值类型" prop="charge_type">
            <el-select size="mini" v-model="ruleForm.charge_type" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in chargetypeList"
                :key="item.id"
                :label="item.type_name_cn"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="充值金额" prop="charge_value">
            <el-input size="small" v-model="ruleForm.charge_value"/>
          </el-form-item>
          <el-form-item label="启用状态" required>
            <el-switch size="small"
              v-model="ruleForm.status"
              :active-value="1"
              :inactive-value="0"
              active-color="#13ce66"
              inactive-color="#ff4949"/>
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
          <el-form-item label="游戏名称" prop="game">
            <el-select size="mini" v-model="ruleForm_patch.game" placeholder="请选择游戏" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in gameList"
                :key="item.game"
                :label="item.game_name_cn"
                :value="item.game">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="充值类型" prop="charge_type">
            <el-select size="mini" v-model="ruleForm_patch.charge_type" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option
                v-for="item in chargetypeList"
                :key="item.id"
                :label="item.type_name_cn"
                :value="item.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="充值金额" prop="charge_value">
            <el-input size="small" v-model="ruleForm_patch.charge_value"/>
          </el-form-item>
          <el-form-item label="启用状态" prop="status">
            <el-switch size="small"
              v-model="ruleForm_patch.status"
              :active-value="1"
              :inactive-value="0"
              active-color="#13ce66"
              inactive-color="#ff4949" />
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
  name: 'price',
  components: { Mysearch, Pagination },
  data() {
    return {
      page_datas: [],
      gameList: [],
      chargetypeList: [],
      testList: [],
      centerDialog: false,
      centerDialog_patch: false,
      centerDialog_delete: false,
      my_pagination: {
        page: 1,
        page_size: 10,
        count: 0,
        search: '',
        search_type: '',
      },
      ruleForm: {
        status: 1
      },
      ruleForm_patch: {},
      rules: {
        game: [
          { required: true, message: '请选择游戏', trigger: 'change' }
        ],
        charge_type: [
          { required: true, message: '请选择充值类型', trigger: 'change' }
        ]
      },
      rules_patch: {
        
      },
      delete_data: {},
    }
  },

  computed: {
    isGetUser() {
      return ['SuperAdmin', 'Admin'].includes(this.$store.getters.user_obj.group.group_type) || this.$store.getters.auth_json.user.auth_list
    }
  },

  created: function() {
    this.get_need_data(this.my_pagination)
    this.get_authGame_data()
    this.get_chargetype_data()
  },

  methods: {
    get_need_data(params) {
      GetAjax('/price/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },

    get_chargetype_data(params) {
      GetAjax('/chargetype/', params).then(response => {
        this.chargetypeList = response.data
      })
    },

    get_authGame_data(params) {
      GetAjax('/authGame/', params).then(response => {
        this.gameList = this.distinctGame(response.data)
      })
    },

    // 游戏ID去重
    distinctGame(gameData) {
      const result = []
      const gameIds = []
      gameData.forEach(element => {
        if (!gameIds.includes(element.game)) {
          gameIds.push(element.game)
          result.push(element)
        }
      })
      return result
    },

    post_need_data(data) {
      PostAjax('/price/', data).then(response => {
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
      PatchAjax('/price/' + data.id + '/', data).then(response => {
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
      DeleteAjax('/price/' + data.id + '/', data).then(response => {
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

<style lang='scss' scoped>
.time-picker {
  width: 150px;
}
.tips {
  margin: 10px 0 10px 5px;
  font-size: 12px;
  color: #909399;
}
</style>