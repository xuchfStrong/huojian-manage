
<template>
  <div class="app-container">
    <el-row>
      <el-col :span="10">
        <el-button v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.chargetype.auth_create" size="small" type="primary" @click="new_data">新增</el-button>
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
			<el-table-column prop="type_name_cn" label="类型名称"/>
      <el-table-column prop="type_name" label="类型代码"/>
      <el-table-column prop="vip" label="辅助类型">
        <template slot-scope="scope">
          {{ scope.row.vip | typeFilter }}
        </template>
      </el-table-column>
      <el-table-column prop="vip" label="定义类型">
        <template slot-scope="scope">
          <el-tag :type="scope.row.decide_type?'warning':'success'"> {{ scope.row.decide_type | decideTypeFilter }}</el-tag>
        </template>
      </el-table-column>
			<el-table-column prop="charge_value" label="充值金额"/>
			<el-table-column prop="days" label="充值天数"/>
			<el-table-column prop="content" label="备注"/>
				
      <el-table-column fixed="right" label="操作" align="center" width="150">
        <template slot-scope="scope" v-if="$store.getters.user_obj.group.group_type === 'SuperAdmin' || $store.getters.auth_json.chargetype.auth_update">
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
          <el-form-item label="类型名称" prop="type_name_cn">
            <el-input size="small" v-model="ruleForm.type_name_cn"/>
          </el-form-item>
          <el-form-item label="类型代码" prop="type_name">
            <el-input size="small" v-model="ruleForm.type_name"/>
          </el-form-item>
          <el-form-item label="辅助类型" prop="vip">
            <el-select size="small" v-model="ruleForm.vip" placeholder="请选择辅助类型" filterable clearable style="width: 100%;">
              <el-option label="普通版" :value="0"/>
              <el-option label="VIP版" :value="1"/>
            </el-select>
          </el-form-item>
          <el-form-item label="充值类型" prop="decide_type">
            <el-select size="small" v-model="ruleForm.decide_type" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option label="系统设定" :value="0"/>
              <el-option label="自定义" :value="1"/>
            </el-select>
          </el-form-item>
          <el-form-item label="充值金额" prop="charge_value">
            <el-input size="small" v-model="ruleForm.charge_value"/>
          </el-form-item>
          <el-form-item label="充值天数" prop="days">
            <el-input size="small" v-model="ruleForm.days"/>
          </el-form-item>
          <el-form-item label="备注" prop="content">
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
          <el-form-item label="类型名称" prop="type_name_cn">
            <el-input size="small" v-model="ruleForm_patch.type_name_cn"/>
          </el-form-item>
          <el-form-item label="类型代码" prop="type_name">
            <el-input size="small" v-model="ruleForm_patch.type_name"/>
          </el-form-item>
          <el-form-item label="辅助类型" prop="vip">
            <el-select size="small" v-model="ruleForm_patch.vip" placeholder="请选择辅助类型" filterable clearable style="width: 100%;">
              <el-option label="普通版" :value="0"/>
              <el-option label="VIP版" :value="1"/>
            </el-select>
          </el-form-item>
          <el-form-item label="充值类型" prop="decide_type">
            <el-select size="small" v-model="ruleForm_patch.decide_type" placeholder="请选择充值类型" filterable clearable style="width: 100%;">
              <el-option label="系统设定" :value="0"/>
              <el-option label="自定义" :value="1"/>
            </el-select>
          </el-form-item>
          <el-form-item label="充值金额" prop="charge_value">
            <el-input size="small" v-model="ruleForm_patch.charge_value"/>
          </el-form-item>
          <el-form-item label="充值天数" prop="days">
            <el-input size="small" v-model="ruleForm_patch.days"/>
          </el-form-item>
          <el-form-item label="备注" prop="content">
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
  name: 'chargetype',
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
        type_name_cn: '',
        type_name: '',
        vip: '',
        decide_type: '',
        charge_value: '',
        days: '',
        content: ''
      },
      rules: {
        type_name_cn: [
          { required: true, message: '请输入类型名称', trigger: 'blur' }
        ],
        type_name: [
          { required: true, message: '请输入类型代码', trigger: 'blur' }
        ],
        vip: [
          { required: true, message: '请选择辅助类型', trigger: 'change' }
        ],
        decide_type: [
          { required: true, message: '请选择充值类型', trigger: 'change' }
        ],
        charge_value: [
          { required: true, message: '请输入充值金额', trigger: 'blur' }
        ],
        days: [
          { required: true, message: '请输入充值天数', trigger: 'blur' }
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
      }
    }
  },

  created: function() {
    this.get_need_data(this.my_pagination)
  },

  methods: {
    get_need_data(params) {
      GetAjax('/chargetype/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
      })
    },


    post_need_data(data) {
      PostAjax('/chargetype/', data).then(response => {
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
      PatchAjax('/chargetype/' + data.id + '/', data).then(response => {
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
      DeleteAjax('/chargetype/' + data.id + '/', data).then(response => {
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
