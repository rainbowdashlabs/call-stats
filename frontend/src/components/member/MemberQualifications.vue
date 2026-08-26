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
  <section class="card p-5 flex flex-col gap-4">
    <span class="label">{{ t('members.qualifications.title') }}</span>

    <div v-if="loading" class="text-muted">{{ t('common.loading') }}</div>
    <div v-else-if="member_qualifications.length === 0" class="text-muted text-sm">
      {{ t('members.qualifications.empty') }}
    </div>
    <div v-else class="flex flex-wrap gap-2">
      <span v-for="qualification in member_qualifications" :key="qualification.qualification_id" class="qual">
        <span class="font-condensed font-semibold tracking-wide uppercase text-sm">
          {{ qualificationName(qualification) }}
        </span>
        <span class="tabular text-xs text-muted">{{ qualification.since }}</span>
        <SimpleButton @click="remove(qualification)" :aria-label="t('common.delete')">
          <font-awesome-icon icon="fa-solid fa-xmark"/>
        </SimpleButton>
      </span>
    </div>

    <div v-if="qualifications.length > 0" class="flex flex-wrap items-end gap-3 pt-1">
      <div class="flex flex-col gap-2 grow" style="min-width: 14rem">
        <span class="label">{{ t('members.qualifications.add') }}</span>
        <SmartSelect v-model="selected_qualification" :key-mapper="(v) => v.id!" :value-mapper="(v) => v.name"
                     :options="qualifications" strict/>
      </div>
      <div class="flex flex-col gap-2">
        <span class="label">{{ t('members.qualifications.since') }}</span>
        <DatePicker v-model="selected_date"/>
      </div>
      <ConfirmButton @click="add">{{ t('common.add') }}</ConfirmButton>
    </div>
  </section>
</template>

<style scoped>
.qual {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  height: 30px;
  padding: 0 6px 0 10px;
  border: 1px solid var(--c-rule);
  border-radius: 3px;
  background: var(--c-raised);
}
</style>
