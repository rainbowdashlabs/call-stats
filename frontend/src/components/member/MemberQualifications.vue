<script setup lang="ts">
import {onMounted, type PropType, ref} from "vue";
import type {MemberQualification, Qualification} from "../../interfaces/Qualification.ts";
import type {Member} from "../../interfaces/Member.ts";
import SmartSelect from "../base/select/SmartSelect.vue";
import {addQualification, getQualifications} from "../../api/member.ts";
import {listQualifications} from "../../api/qualifications.ts";
import ConfirmButton from "../base/buttons/derivates/ConfirmButton.vue";
import {parseDate} from "../../scripts/datetime.ts";

const props = defineProps({
  member: {
    type: Object as PropType<Member>,
    required: true
  }
})
const member_qualifications = ref<MemberQualification[]>([])
const qualifications = ref<Qualification[]>([])

const selected_qualification = ref<Qualification>({id: -1, name: "loading..."})
const selected_date = ref<string>(new Date().toISOString().split('T')[0]!)

function qualificationName(qualification: MemberQualification): String {
  let index = qualifications.value.findIndex(v => v.id === qualification.qualification_id)
  return qualifications.value[index]!.name
}

async function add() {
  console.log(selected_date.value)
  let qualification = {
    member_id: props.member.id!,
    qualification_id: selected_qualification.value.id!,
    since: parseDate(selected_date.value)
  }
  console.log(qualification)
  await addQualification(qualification)
  member_qualifications.value.push(qualification)
}

async function load() {
  member_qualifications.value = await getQualifications(props.member)
  qualifications.value = await listQualifications()
  selected_qualification.value = qualifications.value[0]!
  console.log(JSON.stringify(qualifications.value))
}

onMounted(load)
</script>

<template>
  <div>
    <div>Qualifications</div>
    <div v-for="qualification in member_qualifications">{{ qualificationName(qualification) }}
      {{ qualification.since }}
    </div>

    <div v-if="qualifications.length > 0" class="flex gap-2">
      <SmartSelect class="grow"
                   :v-model="selected_qualification"
                   :key_mapper="(v) => v.id!"
                   :value_mapper="(v) => v.name!"
                   :options="qualifications"
                   strict/>
      <input type="date" v-model="selected_date">
      <ConfirmButton @click="add">Add</ConfirmButton>
    </div>
  </div>
</template>

<style scoped>

</style>