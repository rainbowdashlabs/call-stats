<script setup lang="ts">
import {onMounted, type PropType, ref} from "vue";
import type {MemberQualification, Qualification} from "../../interfaces/Qualification.ts";
import type {Member} from "../../interfaces/Member.ts";
import SmartSelect from "../base/select/SmartSelect.vue";
import {addQualification, getQualifications, removeQualification} from "../../api/member.ts";
import {listQualifications} from "../../api/qualifications.ts";
import ConfirmButton from "../base/buttons/derivates/ConfirmButton.vue";
import {ADateTime} from "../../scripts/datetime.ts";
import SimpleButton from "../base/buttons/SimpleButton.vue";
import DatePicker from "../base/datetime/DatePicker.vue";
import {t} from "../../i18n";

const props = defineProps({
  member: {
    type: Object as PropType<Member>,
    required: true
  }
})
const member_qualifications = ref<MemberQualification[]>([])
const qualifications = ref<Qualification[]>([])
const loading = ref(true)

const selected_qualification = ref<Qualification>({id: -1, name: t("common.loading")})
const selected_date = ref<ADateTime>(ADateTime.now().withoutTime())

function qualificationName(qualification: MemberQualification): string {
  const match = qualifications.value.find(v => v.id === qualification.qualification_id)
  return match?.name ?? ''
}

async function add() {
  let qualification = {
    member_id: props.member.id!,
    qualification_id: selected_qualification.value.id!,
    since: selected_date.value.toUnixTimestamp()
  }
  qualification = await addQualification(qualification)
  member_qualifications.value.push(qualification)
}

async function load() {
  loading.value = true
  try {
    member_qualifications.value = await getQualifications(props.member)
    qualifications.value = await listQualifications()
    selected_qualification.value = qualifications.value[0]!
  } finally {
    loading.value = false
  }
}

async function remove(qualification :MemberQualification){
  await removeQualification(qualification)
  member_qualifications.value = member_qualifications.value.filter(e => e.qualification_id != qualification.qualification_id)
}

onMounted(load)
</script>

<template>
  <div>
    <div>{{ t('members.qualifications.title') }}</div>
    <div v-if="loading" class="p-2">{{ t('common.loading') }}</div>
    <div v-for="qualification in member_qualifications" class="flex gap-2">
      {{ qualificationName(qualification) }} {{ t('members.qualifications.since') }} {{ qualification.since }}
      <SimpleButton @click="remove(qualification)">🗑️</SimpleButton>
    </div>

    <div v-if="qualifications.length > 0" class="flex gap-2">
      <SmartSelect class="grow"
                   v-model="selected_qualification"
                   :key-mapper="(v) => v.id!"
                   :value-mapper="(v) => v.name"
                   :options="qualifications"
                   strict/>
      <DatePicker v-model="selected_date"/>
      <ConfirmButton @click="add">{{ t('common.add') }}</ConfirmButton>
    </div>
  </div>
</template>

<style scoped>

</style>