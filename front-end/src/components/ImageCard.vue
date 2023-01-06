<template>
  <q-card class="my-card" flat bordered>
    <q-img :src="imageUrl" />
    <q-card-section>
      <div class="q-gutter-md">
        <q-chip v-for="item in tags" :key="item">{{ item }}</q-chip>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "ImageCard",
  props: ["imageUrl", "propTags"],
  data() {
    return {
      tags: [],
    };
  },
  mounted() {
    this.tags = this.propTags;
  },
});
</script>

<style lang="scss" scoped>
</style>