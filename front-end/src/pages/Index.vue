<template>
  <q-page>
    <!--Image Selection Section -->
    <div class="row justify-center q-mt-xl">
      <div class="col-2 text-center">
        <q-avatar
          v-if="selectedPhotoURL == ''"
          size="80px"
          font-size="80px"
          icon="image"
        />
        <q-img v-else :src="selectedPhotoURL" class="photo-preview"> </q-img>
        <input
          style="display: none"
          type="file"
          @change="onFileSelected"
          ref="photoInput"
        />
      </div>
      <div class="col-2 text-center">
        <q-btn
          label="Pick Photo"
          class="pick-button"
          outline
          type="submit"
          @keydown.enter.prevent
          @click="$refs.photoInput.click()"
        />
      </div>
      <div class="col-2">
        <q-option-group
          :options="options"
          type="checkbox"
          v-model="tags"
        ></q-option-group>
      </div>
    </div>
    <!--Card Upload Section -->
    <div class="row justify-center q-mt-xl q-mb-lg">
      <q-btn
        label="Upload"
        outline
        type="submit"
        @keydown.enter.prevent
        @click="savePhoto"
      />
    </div>
    <div
      v-if="message"
      class="alert row justify-center q-mt-xl q-mb-lg"
      role="alert"
    >
      {{ message }}
    </div>
    <q-separator inset />
    <!--Library Section -->
    <div class="row q-mt-xl q-mb-lg">
      <div v-for="(item, index) in cardList" :key="index" class="col-3 q-pa-lg">
        <image-card
          :imageUrl="item.imageUrl"
          :propTags="item.tags"
        ></image-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from "vue";
import { api } from "../boot/axios";
import ImageCard from "components/ImageCard.vue";
import { Buffer } from "buffer";

export default defineComponent({
  name: "PageIndex",
  components: { ImageCard },
  data() {
    return {
      selectedPhoto: null,
      selectedPhotoURL: "",
      message: "",
      cardList: [],
      tags: [],
      options: [
        { label: "Person", value: "person" },
        { label: "Place", value: "place" },
        { label: "Thing", value: "thing" },
      ],
      tempList = [
        {
          imageUrl: "https://cdn.quasar.dev/img/parallax2.jpg",
          tags: ["person"],
        },
        {
          imageUrl: "https://cdn.quasar.dev/img/parallax2.jpg",
          tags: ["place"],
        },
        {
          imageUrl: "https://cdn.quasar.dev/img/parallax2.jpg",
          tags: ["thing"],
        },
        {
          imageUrl: "https://cdn.quasar.dev/img/parallax2.jpg",
          tags: ["person", "place"],
        },
        {
          imageUrl: "https://cdn.quasar.dev/img/parallax2.jpg",
          tags: ["person", "place"],
        },
      ]
    };
  },
  mounted() {
    this.retrieveAllPhotos();
  },
  methods: {
    //import photo from file selection
    onFileSelected(event) {
      const target = event.target;
      if (target.files != null && target.files.length >= 1) {
        this.selectedPhoto = target.files[0];
        if (this.selectedPhoto == null) return;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedPhotoURL = e.target?.result;
        };
        reader.readAsDataURL(this.selectedPhoto);
      }
    },
    //confirm photo is selected and size is correct
    savePhoto() {
      if (this.selectedPhoto == null) {
        this.message = "Please choose a file first";
        return;
      }
      if (this.selectedPhoto.size > 3 * 1024 * 1024) {
        this.message = "File too large. Max size 3 Mb";
        return;
      }
      this.message = "";
      this.uploadPhoto(this.selectedPhoto, this.tags);
    },
    //upload photo to mongo and photo ids and tags to tigergraph
    uploadPhoto(photo, tags) {
      const formData = new FormData();
      formData.append("file", photo, photo.name);
      formData.append("tags", tags);
      api
        .post("/uploadPhoto/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then(
          this.cardList.push({ imageUrl: this.selectedPhotoURL, tags: tags }),
          (this.selectedPhoto = null),
          (this.selectedPhotoURL = ""),
          (this.tags = [])
        );
    },
    // retrieve Photo by id and store its URL in libraryPhotoURLs[idx]
    retrievePhoto(id, idx) {
      api
        .put(`/retrievePhoto/${id}`, {})
        .then((resp) => {
          const buff = Buffer.from(resp.data, "base64");
          const blob = new Blob([buff], { type: "image/png" });
          const photo = new File([blob], "test", { type: "image/png" });
          const reader = new FileReader();
          reader.onload = (e) => {
            this.cardList[idx]["imageUrl"] = e.target?.result;
          };
          reader.readAsDataURL(photo);
        })
        .catch((err) => {
          console.log(err);
        });
    },
    //retrieve all photo ids and tags
    retrieveAllPhotos() {
      this.cardList = [];
      api
        .put("/retrieveAllPhotoInfo", {})
        .then((resp) => {
          const allPhotoInfo = resp.data.data;
          for (let i = 0; i < allPhotoInfo.length; i++) {
            this.cardList.push({
              imageUrl: "",
              tags: allPhotoInfo[i]["attributes"]["@tags"],
            });
            this.retrievePhoto(allPhotoInfo[i]["v_id"], i);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
});
</script>

<style lang="scss" scoped>
.pick-button {
  height: 40px;
  margin-top: 15px;
  margin-bottom: 10px;
}
.photo-preview {
  width: 80px;
  max-width: 100%;
  height: 80px;
  max-height: 100%;
  border-radius: 50%;
  margin-right: 10%;
  margin-left: 20%;
  border-radius: 16px;
}
.alert {
  color: red;
  text-align: center;
}
</style>
