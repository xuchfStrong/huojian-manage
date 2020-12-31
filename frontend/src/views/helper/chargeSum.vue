
<template>
  <div class="app-container">
    <el-form :inline="true" size="mini" class="search_form_wrapper_small" label-width="50px"  label-position="right">
      <el-button type="primary" size="mini" @click="to_search" class="btn-form-item">搜索</el-button>

      <el-form-item label="用户:" v-if="isGetUser">
        <el-select size="mini" v-model="my_pagination.user_id" placeholder="请选择用户" filterable clearable style="width: 100%;">
          <el-option
            v-for="item in userList"
            :key="item.id"
            :label="item.username"
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
      
      <el-form-item label="开始:">
        <el-date-picker
          v-model="my_pagination.start_time"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="充值开始日期"
          class="time-picker">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="结束:">
        <el-date-picker
          v-model="my_pagination.end_time"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="充值结束日期"
          class="time-picker">
        </el-date-picker>
      </el-form-item>
    </el-form>
    <div class="tips">提示：默认统计最近7天的数据，不包括当天。</div>
    <el-table
      :data="page_datas"
      size="mini"
      show-summary
      border
      stripe
      style="width: 100%">
			<el-table-column prop="game__game_name_cn" label="游戏名"/>
      <el-table-column prop="user__username" label="用户名"/>
      <el-table-column prop="day" label="日期"/>
			<el-table-column prop="charge_value" label="金额"/>
    </el-table>
  </div>
</template>

<script>
import store from '@/store'
import { GetAjax, PostAjax, PatchAjax, DeleteAjax } from '@/api/myapi'
import Mysearch from '@/components/SearchField/index2.vue'

export default {
  name: 'chargeSum',
  components: { Mysearch },
  data() {
    return {
      page_datas: [],
      gameList: [],
      userList: [],
      my_pagination: {
      }
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
    this.get_user_data()
  },

  methods: {
    get_need_data(params) {
      GetAjax('/chargeSum/', params).then(response => {
        const data = response.data
        this.page_datas = data
        this.my_pagination.count = response.count
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

    get_user_data(params) {
      if (this.isGetUser) {
        GetAjax('/userofauth/', params).then(response => {
          this.userList = response.data
        })
      }
    },

    getSummaries(param) {
      const { columns, data } = param;
      const sums = [];
      columns.forEach((column, index) => {
        if (index === 0) {
          sums[index] = '总额';
          return;
        }
        const values = data.map(item => Number(item[column.property]));
        if (!values.every(value => isNaN(value))) {
          sums[index] = values.reduce((prev, curr) => {
            const value = Number(curr);
            if (!isNaN(value)) {
              return prev + curr;
            } else {
              return prev;
            }
          }, 0);
          sums[index] += ' 元';
        } else {
          sums[index] = 'N/A';
        }
      });

      return sums;
    },

    // 搜索层相关
    to_search() {
      this.my_pagination.page = 1
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